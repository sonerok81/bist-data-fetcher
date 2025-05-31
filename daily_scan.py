import pandas as pd
from datetime import datetime, timedelta
from pipeline import run_pipeline
import json
import os

def save_daily_results(results_df):
    """Günlük sonuçları JSON formatında kaydeder"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Sonuçları dictionary formatına çevir
    results_dict = results_df.to_dict(orient='records')
    
    # Dosya yolu
    file_path = f'data/daily_scans/{today}.json'
    
    # Klasör yoksa oluştur
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Sonuçları kaydet
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'stocks': results_dict
        }, f, ensure_ascii=False, indent=4)
    
    return file_path

def get_market_status():
    """Borsa açık mı kontrol eder"""
    now = datetime.now()
    
    # Hafta sonu kontrolü
    if now.weekday() >= 5:  # 5=Cumartesi, 6=Pazar
        return False
    
    # Saat kontrolü (10:00-18:00)
    market_start = now.replace(hour=10, minute=0, second=0, microsecond=0)
    market_end = now.replace(hour=18, minute=0, second=0, microsecond=0)
    
    return market_start <= now <= market_end

def main():
    # Borsa açık mı kontrol et
    if not get_market_status():
        print("Borsa şu anda kapalı. Tarama yapılmadı.")
        return
    
    print(f"Günlük tarama başlatılıyor... ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    
    try:
        # Pipeline'ı çalıştır
        results = run_pipeline()
        
        if results.empty:
            print("Hiç hisse kriterleri karşılamadı.")
            return
        
        # Sonuçları kaydet
        file_path = save_daily_results(results)
        print(f"Sonuçlar kaydedildi: {file_path}")
        
        # Özet bilgileri göster
        print("\nGünlük Tarama Özeti:")
        print(f"Toplam Hisse Sayısı: {len(results)}")
        print("\nEn Yüksek Sharpe Oranlı Hisseler:")
        print(results.nlargest(3, 'Sharpe')[['Ticker', 'Sharpe', 'Weight']])
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    main() 