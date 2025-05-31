# BIST Tarama Sistemi

Bu proje, Borsa İstanbul'daki hisseleri çeşitli teknik ve istatistiksel kriterlere göre tarayan ve en uygun hisseleri seçen bir sistemdir.

## Özellikler

- Günlük otomatik tarama
- Teknik analiz göstergeleri (RSI, MACD, Bollinger Bands)
- Risk-getiri analizi (Sharpe ve Sortino oranları)
- GARCH tabanlı volatilite analizi
- Streamlit web arayüzü
- Geçmiş tarama sonuçlarını görüntüleme
- Portföy optimizasyonu

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Streamlit uygulamasını başlatın:
```bash
streamlit run streamlit_app.py
```

## Kullanım

### Web Arayüzü
1. Streamlit uygulamasını başlatın
2. "Şimdi Tara" butonuna tıklayarak manuel tarama yapın
3. Geçmiş taramaları görüntülemek için sol menüden tarih seçin

### Günlük Tarama
Günlük tarama sonuçları `data/daily_scans/` klasöründe JSON formatında saklanır.

## Filtreleme Kriterleri

- Sharpe Oranı >= 0.3
- Sortino Oranı >= 0.8
- ATR: %0.1 - %10 arası
- Minimum Fiyat: 1 TL
- Minimum Günlük Hacim: 1M TL
- Teknik Göstergeler:
  - RSI: 30-90 arası
  - MACD: Pozitif
  - Bollinger Bands: Orta bandın üstünde

## Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: X'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 