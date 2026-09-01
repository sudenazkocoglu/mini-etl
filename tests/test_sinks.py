import tempfile
import sqlite3
from pathlib import Path
from mini_etl.sinks import CSVSink, SQLiteSink

def test_csv_sink():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        temp_name = f.name
    
    try:
        sink = CSVSink(temp_name, ["id", "val"])
        sink.write({"id": 1, "val": "test"})
        sink.close()

        text = Path(temp_name).read_text(encoding="utf-8")
        assert "id,val" in text
        assert "1,test" in text
    finally:
        Path(temp_name).unlink(missing_ok=True)

def test_sqlite_sink():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        temp_name = f.name
    
    try:
        sink = SQLiteSink(temp_name, "items")
        sink.write({"id": 10, "name": "Box"})
        sink.close()

        conn = sqlite3.connect(temp_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM items")
        row = cursor.fetchone()
        conn.close()

        assert row == ("10", "Box")
    finally:
        Path(temp_name).unlink(missing_ok=True)