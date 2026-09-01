import yaml
import typer
from pathlib import Path
from typing import Dict, Any

from .sources import CSVSource, JSONLSource, HttpApiSource
from .transforms import MapTransform, FilterTransform, RenameTransform, CastTransform
from .sinks import CSVSink, SQLiteSink, StdoutSink
from .engine import ETLEngine

app = typer.Typer(help="Mini-ETL CLI Framework")

@app.command()
def run(config: str = typer.Option(..., "--config", "-c", help="Path to YAML pipeline configuration file")) -> None:
    """YAML konfigürasyon dosyası ile ETL pipeline'ını çalıştırır."""
    config_path = Path(config)
    if not config_path.exists():
        typer.echo(f"Error: Configuration file '{config_path}' not found.", err=True)
        raise typer.Exit(code=1)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # 1. Source Kurulumu
    src_cfg = cfg.get("source", {})
    src_type = src_cfg.get("type")
    src_path = src_cfg.get("path")
    src_url = src_cfg.get("url")

    source: Any = None
    if src_type == "csv":
        source = CSVSource(src_path)
    elif src_type == "jsonl":
        source = JSONLSource(src_path)
    elif src_type == "http":
        source = HttpApiSource(src_url)
    else:
        typer.echo(f"Error: Unknown source type '{src_type}'", err=True)
        raise typer.Exit(code=1)

    # 2. Transform Kurulumu (Zincirleme)
    transforms_cfg = cfg.get("transforms", [])
    transform_chain = None

    for t_cfg in transforms_cfg:
        t_type = t_cfg.get("type")
        current_transform: Any = None

        if t_type == "filter":
            expr = t_cfg.get("expr")
            # Güvenli küçük bir eval/lambda sarmalayıcı (ör: lambda r: int(r['age']) > 18)
            pred = eval(expr)
            current_transform = FilterTransform(pred)
        elif t_type == "rename":
            mapping = t_cfg.get("mapping", {})
            current_transform = RenameTransform(mapping)
        elif t_type == "cast":
            mapping_raw = t_cfg.get("mapping", {})
            # Örnek: {"age": "int"} -> {"age": int}
            type_map = {k: eval(v) for k, v in mapping_raw.items()}
            current_transform = CastTransform(type_map)

        if current_transform:
            if transform_chain is None:
                transform_chain = current_transform
            else:
                transform_chain = transform_chain >> current_transform

    # 3. Sink Kurulumu
    sink_cfg = cfg.get("sink", {})
    sink_type = sink_cfg.get("type")
    sink: Any = None

    if sink_type == "csv":
        sink = CSVSink(sink_cfg.get("path"), sink_cfg.get("fieldnames", []))
    elif sink_type == "sqlite":
        sink = SQLiteSink(sink_cfg.get("path"), sink_cfg.get("table", "output"))
    elif sink_type == "stdout":
        sink = StdoutSink()
    else:
        typer.echo(f"Error: Unknown sink type '{sink_type}'", err=True)
        raise typer.Exit(code=1)

    # 4. Engine Çalıştırma
    engine_cfg = cfg.get("engine", {})
    engine = ETLEngine(
        source=source,
        transform=transform_chain,
        sink=sink,
        dead_letter_path=engine_cfg.get("dead_letter_path"),
        max_retries=engine_cfg.get("max_retries", 3),
        backoff_factor=engine_cfg.get("backoff_factor", 1.0)
    )

    summary = engine.run()
    typer.echo(f"Pipeline executed successfully: {summary}")

if __name__ == "__main__":
    app()