from turtle import delay

import streamlit as st

from dependecies import (
    question_service,
    correction_service
)

st.title("Correção de Questões")

# ======================================================
# Seleção da questão
# ======================================================

questions = question_service.list_questions()

if not questions:
    st.warning("Nenhuma questão cadastrada.")
    st.stop()

options = {
    q["enunciado"]: q
    for q in questions
}

selected = st.selectbox(
    "Questão",
    list(options.keys())
)

resposta = st.text_area(
    "Resposta do aluno"
)

# ======================================================
# Corrigir
# ======================================================

if st.button("Corrigir", use_container_width=True):

    if not resposta.strip():
        st.warning("Digite a resposta do aluno.")
        st.stop()

    question = options[selected]

    with st.status("🤖 Corrigindo resposta...", expanded=True) as status:

        resultado = correction_service.correct(
            question["questao_id"],
            resposta
        )

        st.write("📝 Gerando avaliação...")

        status.update(
            label="✅ Correção concluída!",
            state="complete"
        )

    st.session_state["correcao"] = {
        "questao_id": question["questao_id"],
        "resposta": resposta,
        "resultado": resultado
    }

    st.rerun()

# ======================================================
# Resultado
# ======================================================

correcao = st.session_state.get("correcao")

if correcao:

    resultado = correcao["resultado"]

    st.divider()

    st.subheader("Avaliação da IA")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Nota sugerida",
            resultado["nota"]
        )

    with col2:
        st.metric(
            "Confiança",
            f"{resultado['confianca']:.1%}"
        )

    st.progress(resultado["confianca"])

    st.write("### Justificativa")

    st.write(resultado["justificativa"])

    # ==================================================
    # Respostas similares
    # ==================================================

    st.divider()

    st.subheader("Respostas similares encontradas")

    exemplos = resultado.get("exemplos", [])

    if len(exemplos) == 0:

        st.info(
            "Nenhuma resposta semelhante encontrada."
        )

    else:

        exemplos = sorted(
            exemplos,
            key=lambda x: x["distancia"]
        )


        if len(exemplos) > 1:

            with st.expander(
                "Respostas semelhantes"
            ):

                for exemplo in exemplos:

                    st.markdown("---")

                    st.write(
                        "**Resposta**"
                    )

                    st.write(
                        exemplo["resposta"]
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            "Nota",
                            exemplo["nota"]
                        )

                    with col2:

                        st.metric(
                            "Similaridade semântica",
                            f"{1 - exemplo['distancia']:.3f}"
                        )

                    st.write(
                        "**Feedback**"
                    )

                    st.write(
                        exemplo["feedback"]
                    )

    # ==================================================
    # Correção final
    # ==================================================

    st.divider()

    st.subheader(
        "Correção Final"
    )

    nota = st.number_input(
        "Nota final",
        min_value=0.0,
        max_value=10.0,
        value=float(resultado["nota"]),
        step=0.5
    )

    feedback = st.text_area(
        "Feedback",
        value=resultado["justificativa"]
    )

    col1, col2 = st.columns(2)

    # ==============================================
    # Aceitar IA
    # ==============================================

    with col1:

        if st.button(
            "Salvar como correção automática",
            use_container_width=True
        ):

            correction_service.save_automatic_correction(

                correcao["questao_id"],

                correcao["resposta"],

                resultado

            )

            del st.session_state["correcao"]

            st.success(
                "Correção salva!"
            )

            st.rerun()

    # ==============================================
    # Correção manual
    # ==============================================

    with col2:

        if st.button(
            "Salvar correção",
            use_container_width=True
        ):

            correction_service.save_manual_correction(

                correcao["questao_id"],

                correcao["resposta"],

                nota,

                feedback

            )

            del st.session_state["correcao"]

            st.success(
                "Correção salva!"
            )

            st.rerun()