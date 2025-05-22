# streamlit_app.py
import streamlit as st
from pipeline import run_pipeline

st.set_page_config(page_title="BIST Pipeline Tarayıcı", layout="wide")
st.title("📈 BIST Hisse Tarayıcı")

st.markdown("""
Bu uygulama, **nikel + teknik + GARCH** tabanlı pipeline’ımızı çalıştırır  
ve hem **tüm taranan hisseleri** hem de **en iyi 3 hisseleri** yan yana gösterir.
""")

if st.button("Çalıştır"):
    with st.spinner("Veriler işleniyor..."):
        df_all = run_pipeline()
        df_top3 = df_all.sort_values('Sharpe', ascending=False).head(3)

    if df_all.empty:
        st.warning("Hiç hisse kriterleri karşılamadı.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔍 Tüm Taranan Hisseler")
            st.dataframe(df_all)
        with col2:
            st.subheader("🏆 En İyi 3 Hisse")
            st.dataframe(df_top3)
