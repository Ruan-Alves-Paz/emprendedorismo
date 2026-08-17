import streamlit as st

from services.QuestionService import QuestionService
from repositories.QuestionRepository import QuestionRepository


repository = QuestionRepository()
service = QuestionService(repository)

st.title("Cadastro de Questões")


enunciado = st.text_area(
    "Enunciado",
    placeholder="""Explique o conceito de X e sua aplicação em Y. Forneça exemplos práticos e discuta as implicações do conceito em diferentes contextos."""
)

resposta_modelo = st.text_area(
    "Resposta modelo",
    placeholder="""O conceito de X é fundamental para entender Y. Ele se aplica em diversas situações, como A, B e C. Além disso, é importante considerar Z ao analisar o conceito."""
)

criterios = st.text_area(
    "Critérios de avaliação",
    height=180,
    placeholder="""
Exemplo:
- O aluno deve demonstrar compreensão do conceito X. 2 pontos
- O aluno deve apresentar um exemplo prático do conceito Y. 3 pontos
- O aluno deve identificar aplicações do conceito Z. 5 pontos
"""
)

nota_maxima = st.number_input(
    "Nota máxima",
    min_value=0,
    value=10
)

if st.button("Salvar"):

    service.create_question(


        enunciado,

        resposta_modelo,
        
        criterios,

        nota_maxima

    )

    st.success("Questão cadastrada!")
    
st.divider()

st.subheader("Questões cadastradas")

questoes = service.list_questions()

st.dataframe(questoes)