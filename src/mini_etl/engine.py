import time
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from .protocols import Source, Transform, Sink

logger = logging.getLogger("mini_etl")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class ETLEngine:
    def __init__(
        self,
        source: Source,
        transform: Optional[Transform] = None,
        sink: Optional[Sink] = None,
        dead_letter_path: Optional[Union[str, Path]] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0
    ) -> None:
        self.source = source
        self.transform = transform
        self.sink = sink
        self.dead_letter_path = Path(dead_letter_path) if dead_letter_path else None
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        self.rows_read = 0
        self.rows_written = 0
        self.rows_rejected = 0
        self._dead_letter_file = None

        if self.dead_letter_path:
            self.dead_letter_path.parent.mkdir(parents=True, exist_ok=True)
            self._dead_letter_file = open(self.dead_letter_path, "w", encoding="utf-8")

    def _write_dead_letter(self, record: Dict[str, Any], error_msg: str) -> None:
        self.rows_rejected += 1
        if self._dead_letter_file:
            payload = {"record": record, "error": error_msg}
            self._dead_letter_file.write(json.dumps(payload) + "\n")

    def _execute_with_retry(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        delay = self.backoff_factor
        for attempt in range(1, self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries:
                    raise
                logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2

    def run(self) -> Dict[str, Union[int, float]]:
        logger.info("ETL Pipeline started.")
        start_time = time.time()

        try:
            raw_iterator = self._execute_with_retry(self.source.read)
            
            for record in raw_iterator:
                self.rows_read += 1
                current_record: Optional[Dict[str, Any]] = record

                if self.transform and current_record is not None:
                    try:
                        current_record = self.transform.process(current_record)
                    except Exception as e:
                        self._write_dead_letter(record, str(e))
                        continue

                if current_record is None:
                    self.rows_rejected += 1
                    continue

                if self.sink:
                    try:
                        self._execute_with_retry(self.sink.write, current_record)
                        self.rows_written += 1
                    except Exception as e:
                        self._write_dead_letter(record, str(e))

        finally:
            if self.sink:
                try:
                    self.sink.close()
                except Exception:
                    pass
            if self._dead_letter_file and not self._dead_letter_file.closed:
                self._dead_letter_file.close()

        duration = time.time() - start_time
        summary: Dict[str, Union[int, float]] = {
            "rows_read": self.rows_read,
            "rows_written": self.rows_written,
            "rows_rejected": self.rows_rejected,
            "duration_seconds": round(duration, 2)
        }
        logger.info(f"ETL Pipeline finished. Summary: {summary}")
        return summary