import csv
import json
import urllib.request
from typing import Iterator, Dict, Any, Union
from pathlib import Path

class CSVSource:
    def __init__(self, filepath: Union[str, Path]) -> None:
        self.filepath = Path(filepath)

    def read(self) -> Iterator[Dict[str, Any]]:
        with open(self.filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield dict(row)

class JSONLSource:
    def __init__(self, filepath: Union[str, Path]) -> None:
        self.filepath = Path(filepath)

    def read(self) -> Iterator[Dict[str, Any]]:
        with open(self.filepath, mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    if isinstance(data, dict):
                        yield data

class HttpApiSource:
    def __init__(self, url: str) -> None:
        self.url = url

    def read(self) -> Iterator[Dict[str, Any]]:
        req = urllib.request.Request(self.url, headers={"User-Agent": "mini-etl"})
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        yield item
            elif isinstance(data, dict):
                yield data