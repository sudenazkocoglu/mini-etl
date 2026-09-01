import csv
import sqlite3
from typing import Dict, Any, Union, List
from pathlib import Path

class CSVSink:
    def __init__(self, filepath: Union[str, Path], fieldnames: List[str]) -> None:
        self.filepath = Path(filepath)
        self.fieldnames = fieldnames
        self.file = open(self.filepath, mode="w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def write(self, record: Dict[str, Any]) -> None:
        filtered = {k: record.get(k, "") for k in self.fieldnames}
        self.writer.writerow(filtered)

    def close(self) -> None:
        if not self.file.closed:
            self.file.close()

class SQLiteSink:
    def __init__(self, db_path: Union[str, Path], table_name: str) -> None:
        self.db_path = Path(db_path)
        self.table_name = table_name
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._table_created = False

    def _init_table(self, record: Dict[str, Any]) -> None:
        columns = [f'"{key}" TEXT' for key in record.keys()]
        cols_def = ", ".join(columns)
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS "{self.table_name}" ({cols_def})')
        self.conn.commit()
        self._table_created = True

    def write(self, record: Dict[str, Any]) -> None:
        if not self._table_created:
            self._init_table(record)
        keys = list(record.keys())
        values = [str(record[k]) if record[k] is not None else "" for k in keys]
        placeholders = ", ".join(["?"] * len(keys))
        cols = ", ".join([f'"{k}"' for k in keys])
        sql = f'INSERT INTO "{self.table_name}" ({cols}) VALUES ({placeholders})'
        self.cursor.execute(sql, values)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

class StdoutSink:
    def write(self, record: Dict[str, Any]) -> None:
        print(record)

    def close(self) -> None:
        pass