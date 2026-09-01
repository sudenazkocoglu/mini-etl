import tempfile
from pathlib import Path
from mini_etl.sources import CSVSource
from mini_etl.sinks import CSVSink
from mini_etl.transforms import MapTransform
from mini_etl.engine import ETLEngine
from mini_etl.protocols import Transform

def test_etl_engine_full_pipeline():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write("val\n5\n10\n")
        src_path = f.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        out_path = f.name

    try:
        source = CSVSource(src_path)
        transform = MapTransform(lambda r: {"val": int(r["val"]) * 2})
        sink = CSVSink(out_path, ["val"])

        engine = ETLEngine(source=source, transform=transform, sink=sink)
        summary = engine.run()

        assert summary["rows_read"] == 2
        assert summary["rows_written"] == 2
        assert summary["rows_rejected"] == 0

        output_text = Path(out_path).read_text(encoding="utf-8")
        assert "val" in output_text
        assert "10" in output_text
        assert "20" in output_text
    finally:
        Path(src_path).unlink(missing_ok=True)
        Path(out_path).unlink(missing_ok=True)

class FailingTransform:
    def process(self, record: dict) -> None:
        raise ValueError("Critical processing error")
    def __rshift__(self, other: Transform) -> Transform:
        return self

def test_engine_dead_letter_on_error():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write("val\n100\n")
        src_path = f.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as f:
        dl_path = f.name

    try:
        source = CSVSource(src_path)
        transform = FailingTransform()  # type: ignore
        engine = ETLEngine(
            source=source,
            transform=transform, # type: ignore
            dead_letter_path=dl_path,
            max_retries=1,
            backoff_factor=0.1
        )
        summary = engine.run()
        assert summary["rows_rejected"] == 1

        dl_content = Path(dl_path).read_text(encoding="utf-8")
        assert "Critical processing error" in dl_content
    finally:
        Path(src_path).unlink(missing_ok=True)
        Path(dl_path).unlink(missing_ok=True) 