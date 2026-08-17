import streamlit as st

st.set_page_config(
    page_title="Correção assistida por IA",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Correção Assistida por IA")

st.markdown("""
Bem-vindo!
Essa aplicação permite que professores cadastrem questões, corrijam respostas de alunos e visualizem o histórico de correções. 
A correção das respostas é realizada com o auxílio de um modelo de linguagem, que avalia a resposta do aluno com base em uma resposta modelo fornecida pelo professor, critérios de avaliação fornecidos pelo professor e questões corrigidas anteriormente.

Utilize o menu lateral para:
- 📚 Cadastrar questões
- 📝 Corrigir respostas
- 📷 Correção por OCR (Imagem)
- 📊 Visualizar histórico
""")