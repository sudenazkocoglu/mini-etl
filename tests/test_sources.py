import json
import tempfile
from pathlib import Path
from mini_etl.sources import CSVSource, JSONLSource

def test_csv_source():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write("name,age\nAli,25\nAyse,30\n")
        temp_name = f.name
    
    try:
        source = CSVSource(temp_name)
        rows = list(source.read())
        assert len(rows) == 2
        assert rows[0] == {"name": "Ali", "age": "25"}
        assert rows[1] == {"name": "Ayse", "age": "30"}
    finally:
        Path(temp_name).unlink(missing_ok=True)

def test_jsonl_source():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl", encoding="utf-8") as f:
        f.write(json.dumps({"id": 1, "val": "a"}) + "\n")
        f.write(json.dumps({"id": 2, "val": "b"}) + "\n")
        temp_name = f.name
    
    try:
        source = JSONLSource(temp_name)
        rows = list(source.read())
        assert len(rows) == 2
        assert rows[0] == {"id": 1, "val": "a"}
        assert rows[1] == {"id": 2, "val": "b"}
    finally:
        Path(temp_name).unlink(missing_ok=True)