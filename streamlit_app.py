# streamlit_app.py

import streamlit as st
from pipeline import run_pipeline

st.set_page_config(page_title="BIST Pipeline Tarayıcı", layout="wide")
st.title("📈 BIST Hisse Tarayıcı")

st.markdown("""
Bu uygulama, **nikel + teknik + GARCH** tabanlı pipeline’ımızı çalıştırır  
ve anlık sinyal listesini gösterir.
""")

if st.button("Çalıştır"):
    with st.spinner("Veriler işleniyor..."):
        df = run_pipeline()
    if df.empty:
        st.warning("Hiç hisse kriterleri karşılamadı.")
    else:
        st.success(f"{len(df)} hisse seçildi:")
        st.dataframe(df)
