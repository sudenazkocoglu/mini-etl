import resource
import tempfile
from pathlib import Path
from mini_etl.sources import CSVSource
from mini_etl.transforms import MapTransform
from mini_etl.sinks import CSVSink
from mini_etl.engine import ETLEngine

def get_max_rss_mb() -> float:
    # ru_maxrss Unix sistemlerde prosesin gördüğü maksimum RAM miktarını KB cinsinden verir
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def run_streaming_benchmark():
    print("--- Mini-ETL Bellek / Streaming Benchmark ---")
    
    row_counts = [10_000, 50_000, 100_000, 500_000]
    
    for row_count in row_counts:
        # Geçici büyük CSV dosyası üretelim
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as src_f:
            src_f.write("id,value\n")
            for i in range(row_count):
                src_f.write(f"{i},data_row_content_{i}\n")
            src_path = src_f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as sink_f:
            sink_path = sink_f.name

        source = CSVSource(src_path)
        transform = MapTransform(lambda row: {"id": row["id"], "value": row["value"].upper()})
        sink = CSVSink(sink_path, fieldnames=["id", "value"])

        engine = ETLEngine(source=source, transform=transform, sink=sink)
        
        # ETL motorunu koştur ve bellek zirvesini ölç
        engine.run()
        mem_peak = get_max_rss_mb()
        
        print(f"Satır Sayısı: {row_count:<8} | Zirve RAM (Peak RSS): {mem_peak:.2f} MB")

        # Temizlik
        Path(src_path).unlink(missing_ok=True)
        Path(sink_path).unlink(missing_ok=True)

if __name__ == "__main__":
    run_streaming_benchmark()