# Mini-ETL Veri İşleme Framework (Ödev 2.2)

Harici kütüphane bağımlılığı olmadan, tamamen standart Python kütüphaneleri (`stdlib`) kullanılarak sıfırdan geliştirilmiş modüler bir **ETL (Extract, Transform, Load)** mini kütüphanesidir.

## ⚙️ Temel Özellikler
- **Protokol Tabanlı Mimari:** `Protocol` yapılarıyla esnek ve sıkı olmayan arayüz tasarımı.
- **Transform Zinciri:** `map`, `filter`, `validate`, `rename`, `cast` operasyonları ve `__rshift__` (`>>`) kompozisyon operatörü.
- **Streaming Desteği:** Büyük veri setlerini düşük RAM tüketimiyle işleme (`Generator` tabanlı akış).
- **Hata Yönetimi ve Dead Letter:** Hatalı satırları sisteme takılmadan `dead_letter` çıktısına yönlendirme ve `exponential backoff` ile retry mekanizması.
- **CLI Entegrasyonu:** `typer` kütüphanesiyle `mini-etl run --config pipeline.yaml` komut desteği.
- **Güvenilirlik:** %85+ test kapsamı, `mypy --strict` tip denetimi ve `Hypothesis` ile property-based testler.

## 🚀 Çalıştırma
```bash
python -m src.mini_etl.cli run --config pipeline.yaml

## Bellek ve Streaming Performansı (Benchmark)
`ru_maxrss` kullanarak yaptığımız bellek tüketim testleri, generator mimarimizin büyük veri setlerini düşük ve sabit RAM tüketimiyle işlediğini kanıtlamaktadır:

| Satır Sayısı | İşlem Süresi | Zirve RAM (Peak RSS) |
|-------------|--------------|----------------------|
| 10,000      | 0.02s        | 34.89 MB             |
| 50,000      | 0.11s        | 34.89 MB             |
| 100,000     | 0.19s        | 34.89 MB             |
| 500,000     | 0.94s        | 34.89 MB             |