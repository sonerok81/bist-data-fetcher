# streamlit_app.py
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pipeline import run_pipeline
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="BIST Tarama Sistemi", layout="wide")

def load_daily_results(date_str):
    """Belirli bir tarihin sonuçlarını yükler"""
    file_path = f'data/daily_scans/{date_str}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_available_dates():
    """Mevcut tarama sonuçlarının tarihlerini döndürür"""
    if not os.path.exists('data/daily_scans'):
        return []
    return sorted([f.replace('.json', '') for f in os.listdir('data/daily_scans') if f.endswith('.json')], reverse=True)

def plot_stock_performance(ticker, days=30):
    """Hisse performans grafiğini çizer"""
    # TODO: Bu fonksiyon gerçek verilerle güncellenecek
    return None

def main():
    st.title("BIST Tarama Sistemi")
    
    # Sidebar
    st.sidebar.title("Kontroller")
    
    # Manuel tarama butonu
    if st.sidebar.button("Şimdi Tara"):
        with st.spinner("Tarama yapılıyor..."):
            results = run_pipeline()
            if not results.empty:
                st.success("Tarama tamamlandı!")
                st.dataframe(results)
            else:
                st.warning("Hiç hisse kriterleri karşılamadı.")
    
    # Tarih seçici
    available_dates = get_available_dates()
    if available_dates:
        selected_date = st.sidebar.selectbox(
            "Tarih Seçin",
            available_dates,
            format_func=lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%d %B %Y')
        )
        
        # Seçilen tarihin sonuçlarını göster
        results = load_daily_results(selected_date)
        if results:
            st.subheader(f"Tarama Sonuçları - {selected_date}")
            
            # DataFrame oluştur
            df = pd.DataFrame(results['stocks'])
            
            # İki sütunlu layout
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Tüm Hisseler")
                st.dataframe(df)
            
            with col2:
                st.write("En İyi 5 Hisse (Sharpe Oranına Göre)")
                top_5 = df.nlargest(5, 'Sharpe')
                st.dataframe(top_5)
                
                # Portföy dağılımı grafiği
                fig = go.Figure(data=[go.Pie(
                    labels=top_5['Ticker'],
                    values=top_5['Weight'],
                    hole=.3
                )])
                fig.update_layout(title="Portföy Dağılımı (Top 5)")
                st.plotly_chart(fig)
            
            # Performans grafikleri
            st.subheader("Hisse Performansları")
            selected_ticker = st.selectbox("Hisse Seçin", df['Ticker'].tolist())
            if selected_ticker:
                performance = plot_stock_performance(selected_ticker)
                if performance:
                    st.plotly_chart(performance)
                else:
                    st.info("Performans verisi henüz mevcut değil.")
    else:
        st.info("Henüz kaydedilmiş tarama sonucu bulunmuyor.")

if __name__ == "__main__":
    main()
