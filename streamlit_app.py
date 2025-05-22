import streamlit as st
from pipeline import run_pipeline

st.set_page_config(page_title="BIST Pipeline Tarayıcı", layout="wide")
st.title("📈 BIST Hisse Tarayıcı")

st.markdown("""
Bu uygulama, **nikel + teknik + GARCH** tabanlı pipeline’ımızı çalıştırır  
ve **Sharpe**’a göre sıralanmış en iyi 3 hisseyi gösterir.
""")

if st.button("Çalıştır"):
    with st.spinner("Veriler işleniyor..."):
        df = run_pipeline()
        # En iyi 3 hisseyi al
        top3 = df.sort_values('Sharpe', ascending=False).head(3)
    if top3.empty:
        st.warning("Hiç hisse kriterleri karşılamadı.")
    else:
        st.success(f"En iyi 3 hisse seçildi:")
        st.dataframe(top3)
