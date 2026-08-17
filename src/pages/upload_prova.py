import tempfile
import os
import streamlit as st

from dependecies import (
    ocr_extractor,
    question_service,
    correction_service,
    exam_repository
)

st.set_page_config(page_title="Correção por OCR", page_icon="📷", layout="wide")

st.title("📷 Correção de Prova por Imagem (OCR)")
st.markdown("""
Faça upload da foto da prova discursiva respondida pelo aluno. 
O sistema extrairá o nome do aluno e as respostas das questões utilizando **OCR com IA**, permitindo a revisão do texto antes da correção automática.
""")

# ======================================================
# 1. Upload de Imagem
# ======================================================

uploaded_file = st.file_uploader(
    "Selecione uma imagem da prova (.png, .jpg, .jpeg)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Imagem enviada", use_column_width=True)

    col_ocr, col_clear = st.columns([2, 1])

    with col_ocr:
        if st.button("🔍 Extrair Texto (OCR)", use_container_width=True):
            with st.spinner("🤖 Processando imagem com OCR..."):
                # Salva arquivo temporário
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                try:
                    ocr_result = ocr_extractor.extract(tmp_file_path)
                    st.session_state["ocr_result"] = ocr_result
                    # Limpa avaliação anterior se houver
                    if "resultado_prova" in st.session_state:
                        del st.session_state["resultado_prova"]
                    st.success("Texto extraído com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao processar OCR: {e}")
                finally:
                    if os.path.exists(tmp_file_path):
                        os.remove(tmp_file_path)
            st.rerun()

    with col_clear:
        if st.button("Limpar", use_container_width=True):
            if "ocr_result" in st.session_state:
                del st.session_state["ocr_result"]
            if "resultado_prova" in st.session_state:
                del st.session_state["resultado_prova"]
            st.rerun()

# ======================================================
# 2. Revisão do Texto Extraído (Human-in-the-Loop)
# ======================================================

ocr_result = st.session_state.get("ocr_result")

if ocr_result:
    st.divider()
    st.subheader("📝 Revisão do Texto Extraído")
    st.info("Verifique e corrija eventuais erros de leitura do OCR antes de submeter para avaliação.")

    aluno_nome = st.text_input(
        "Nome do Aluno",
        value=ocr_result.get("aluno", "Aluno Não Identificado")
    )

    questoes_extraidas = ocr_result.get("questoes", [])

    if not questoes_extraidas:
        st.warning("Nenhuma questão foi identificada na imagem.")
    else:
        respostas_editadas = []

        available_questions = question_service.list_questions()
        question_map = {q["questao_id"]: q for q in available_questions}

        for idx, q_ext in enumerate(questoes_extraidas):
            q_id = q_ext.get("questao_id", idx + 1)
            q_resp = q_ext.get("resposta_aluno", "")

            with st.expander(f"Questão {q_id}", expanded=True):
                # Caso a questão exista no cadastro, mostra o enunciado
                if q_id in question_map:
                    st.markdown(f"**Enunciado:** {question_map[q_id]['enunciado']}")
                else:
                    st.caption(f"Questão ID {q_id} não cadastrada previamente.")

                resposta_texto = st.text_area(
                    f"Resposta do aluno (Questão {q_id})",
                    value=q_resp,
                    key=f"ocr_resp_{idx}"
                )

                respostas_editadas.append({
                    "questao_id": q_id,
                    "resposta_aluno": resposta_texto
                })

        if st.button("🤖 Avaliar Prova com IA", use_container_width=True):
            with st.status("🤖 Avaliando respostas da prova...", expanded=True) as status:
                questoes_avaliadas = []
                nota_total = 0

                for item in respostas_editadas:
                    q_id = item["questao_id"]
                    resp_aluno = item["resposta_aluno"]

                    if q_id not in question_map:
                        st.warning(f"Questão ID {q_id} não encontrada no cadastro de questões. Pulando...")
                        continue

                    st.write(f"Avaliando Questão {q_id}...")
                    resultado = correction_service.correct(q_id, resp_aluno)

                    questoes_avaliadas.append({
                        "questao_id": q_id,
                        "resposta_aluno": resp_aluno,
                        "nota": resultado["nota"],
                        "justificativa": resultado["justificativa"],
                        "confianca": resultado["confianca"],
                        "exemplos": resultado.get("exemplos", [])
                    })
                    nota_total += resultado["nota"]

                status.update(label="✅ Avaliação da prova concluída!", state="complete")

            st.session_state["resultado_prova"] = {
                "aluno": aluno_nome,
                "nota_final": nota_total / len(questoes_avaliadas) if questoes_avaliadas else 0,
                "questoes": questoes_avaliadas
            }
            st.rerun()

# ======================================================
# 3. Resultado da Avaliação da Prova
# ======================================================

resultado_prova = st.session_state.get("resultado_prova")

if resultado_prova:
    st.divider()
    st.subheader(f"📊 Resultado da Avaliação - {resultado_prova['aluno']}")
    st.metric("Nota Geral Média", f"{resultado_prova['nota_final']:.1f}")

    questoes_finais = []

    for idx, q_eval in enumerate(resultado_prova["questoes"]):
        st.markdown(f"### Questão {q_eval['questao_id']}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nota Sugerida pela IA", q_eval["nota"])
        with col2:
            st.metric("Confiança da IA", f"{q_eval['confianca']:.1%}")

        st.progress(q_eval["confianca"])

        st.write("**Justificativa da IA:**")
        st.write(q_eval["justificativa"])

        # Respostas similares RAG
        exemplos = q_eval.get("exemplos", [])
        if exemplos:
            with st.expander("Precedentes / Respostas similares (RAG)"):
                for ex in exemplos:
                    st.markdown("---")
                    st.write(f"**Resposta Exemplo:** {ex['resposta']}")
                    st.write(f"**Nota:** {ex['nota']} | **Similaridade:** {1 - ex['distancia']:.3f}")
                    st.write(f"**Feedback:** {ex['feedback']}")

        # Ajuste do Professor
        st.write("**Ajuste Final do Professor:**")
        nota_final_q = st.number_input(
            f"Nota Final (Questão {q_eval['questao_id']})",
            min_value=0.0,
            max_value=10.0,
            value=float(q_eval["nota"]),
            step=0.5,
            key=f"nota_final_{idx}"
        )

        feedback_final_q = st.text_area(
            f"Feedback Final (Questão {q_eval['questao_id']})",
            value=q_eval["justificativa"],
            key=f"feedback_final_{idx}"
        )

        questoes_finais.append({
            "questao_id": q_eval["questao_id"],
            "resposta_aluno": q_eval["resposta_aluno"],
            "nota": nota_final_q,
            "feedback": feedback_final_q,
            "confianca": q_eval["confianca"],
            "origem": "manual" if (nota_final_q != q_eval["nota"] or feedback_final_q != q_eval["justificativa"]) else "automatica"
        })
        st.markdown("---")

    col_save, col_cancel = st.columns(2)

    with col_save:
        if st.button("💾 Salvar Correções no Histórico e RAG", use_container_width=True):
            # Salvar no ExamRepository
            prova_doc = {
                "prova_id": len(exam_repository.get_all()) + 1,
                "aluno": resultado_prova["aluno"],
                "nota_final": sum(q["nota"] for q in questoes_finais) / len(questoes_finais) if questoes_finais else 0,
                "questoes": questoes_finais
            }
            exam_repository.add(prova_doc)

            # Salvar cada questão corrigida na base vetorial e histórico
            for qf in questoes_finais:
                correction_service.save_manual_correction(
                    qf["questao_id"],
                    qf["resposta_aluno"],
                    qf["nota"],
                    qf["feedback"]
                )

            st.success("Prova e correções salvas com sucesso!")
            del st.session_state["ocr_result"]
            del st.session_state["resultado_prova"]
            st.rerun()

    with col_cancel:
        if st.button("Descartar", use_container_width=True):
            del st.session_state["resultado_prova"]
            st.rerun()
