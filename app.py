import streamlit as st
from ufrgs_corretor import grade_ufrgs

st.set_page_config(page_title="Corretor de Redações UFRGS", layout="wide")

st.title("📝 Corretor de Redações - UFRGS")
st.write("Cole abaixo sua redação e as palavras-chave do tema para receber a avaliação no modelo UFRGS.")

# Input de palavras-chave
keywords = st.text_input("Palavras-chave do tema (separe por vírgulas):", "inclusão digital,educação,desigualdade")

# Input da redação
essay = st.text_area("Digite sua redação aqui:", height=400)

# Botão para corrigir
if st.button("Corrigir Redação"):
    if essay.strip():
        tema = [k.strip() for k in keywords.split(",") if k.strip()]
        result = grade_ufrgs(essay, tema)

        st.subheader("📊 Resultado da Correção")
        st.write(f"**Expressão (até 50 pts):** {result['expressao_total_50']}")
        st.write(f"**Estrutura & Conteúdo (até 50 pts):** {result['estrutura_conteudo_total_50']}")
        st.write(f"**Total (0–100):** {result['total_100']}")
        st.write(f"**Nota na escala UFRGS (0–25):** {result['total_escala_25']}")

        st.subheader("🔍 Detalhamento dos critérios")
        st.json(result["detalhes_expressao"])
        st.json(result["detalhes_estrutura_conteudo"])
    else:
        st.warning("Por favor, cole uma redação para corrigir.")
