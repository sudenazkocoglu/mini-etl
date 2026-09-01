import tempfile
from pathlib import Path
import yaml
from typer.testing import CliRunner
from mini_etl.cli import app

runner = CliRunner()

def test_cli_run_success():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write("val\n10\n20\n")
        src_path = f.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        out_path = f.name

    config_data = {
        "source": {"type": "csv", "path": src_path},
        "transforms": [
            {"type": "cast", "mapping": {"val": "int"}}
        ],
        "sink": {"type": "csv", "path": out_path, "fieldnames": ["val"]}
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        result = runner.invoke(app, ["--config", config_path])
        assert result.exit_code == 0
        assert "Pipeline executed successfully" in result.output
    finally:
        Path(src_path).unlink(missing_ok=True)
        Path(out_path).unlink(missing_ok=True)
        Path(config_path).unlink(missing_ok=True)

def test_cli_config_not_found():
    result = runner.invoke(app, ["--config", "nonexistent_file.yaml"])
    assert result.exit_code == 1
    assert "not found" in result.output

def test_cli_unknown_source():
    config_data = {
        "source": {"type": "unknown_type", "path": "dummy.csv"},
        "sink": {"type": "stdout"}
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f)
        config_path = f.name
    try:
        result = runner.invoke(app, ["--config", config_path])
        assert result.exit_code == 1
        assert "Unknown source type" in result.output
    finally:
        Path(config_path).unlink(missing_ok=True)

def test_cli_unknown_sink():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write("val\n10\n")
        src_path = f.name
    config_data = {
        "source": {"type": "csv", "path": src_path},
        "sink": {"type": "unknown_sink"}
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f)
        config_path = f.name
    try:
        result = runner.invoke(app, ["--config", config_path])
        assert result.exit_code == 1
        assert "Unknown sink type" in result.output
    finally:
        Path(src_path).unlink(missing_ok=True)
        Path(config_path).unlink(missing_ok=True)