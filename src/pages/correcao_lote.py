import tempfile
import os
import json
import streamlit as st

from dependecies import (
    ocr_extractor,
    correction_service,
    exam_repository,
    exam_model_service,
    exam_correction_service
)

st.set_page_config(page_title="Correção em Lote", page_icon="👥", layout="wide")

st.title("👥 Correção de Provas em Lote (Vários Alunos)")
st.markdown("""
Avalie provas de uma turma inteira de forma automatizada. 
Você pode enviar **múltiplas fotos de provas** (Batch OCR) ou subir um arquivo **JSON com as respostas da turma**.
""")

# ======================================================
# 1. Seleção do Modelo de Prova
# ======================================================

provas_modelo = exam_model_service.list_exam_models()

if not provas_modelo:
    st.warning("⚠️ Nenhuma prova modelo encontrada. Crie uma prova na página **Criador de Provas** antes de realizar a correção em lote.")

modelo_options = {}
for pm in provas_modelo:
    label = f"📝 {pm.get('titulo', 'Sem Título')} ({pm.get('disciplina', 'Geral')}) - {len(pm.get('questoes', []))} questões"
    modelo_options[label] = pm

selected_modelo_label = st.selectbox(
    "Selecione a Prova Modelo Aplicada à Turma",
    options=list(modelo_options.keys()) if modelo_options else ["Nenhum Modelo"],
    disabled=not bool(provas_modelo)
)

selected_prova_modelo = modelo_options.get(selected_modelo_label) if bool(provas_modelo) else None

if selected_prova_modelo:
    st.info(f"**Modelo Selecionado:** {selected_prova_modelo.get('titulo')} | **Nota Total da Prova:** {selected_prova_modelo.get('nota_total_maxima', 10.0)} pt(s) | **Questões:** {len(selected_prova_modelo.get('questoes', []))}")

st.divider()

# ======================================================
# 2. Métodos de Envio em Lote (Tabs)
# ======================================================

tab_fotos, tab_json = st.tabs(["📷 Múltiplas Fotos (Batch OCR)", "📄 Upload JSON da Turma"])

with tab_fotos:
    st.subheader("📷 Upload de Fotos de Vários Alunos")
    uploaded_files = st.file_uploader(
        "Selecione uma ou mais imagens de provas (.png, .jpg, .jpeg)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"📁 **{len(uploaded_files)} arquivos selecionados.**")

        if st.button("🤖 Processar OCR e Avaliar Provas da Turma", type="primary", use_container_width=True):
            if not selected_prova_modelo:
                st.error("Por favor, selecione uma prova modelo antes de continuar.")
            else:
                progress_bar = st.progress(0.0)
                status_text = st.empty()
                resultados_turma = []

                total_files = len(uploaded_files)

                for idx, file_obj in enumerate(uploaded_files, start=1):
                    status_text.markdown(f"⏳ **Processando Aluno {idx} de {total_files}** ({file_obj.name})...")
                    progress_bar.progress(idx / total_files)

                    # Salva temporário
                    suffix = os.path.splitext(file_obj.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(file_obj.getvalue())
                        tmp_path = tmp.name

                    try:
                        # Extrai via OCR
                        ocr_data = ocr_extractor.extract(tmp_path, prova_modelo=selected_prova_modelo)
                        
                        # Injeta nota maxima do modelo se não houver
                        model_q_map = {q["questao_id"]: q for q in selected_prova_modelo.get("questoes", [])}
                        for q in ocr_data.get("questoes", []):
                            q_id = q.get("questao_id")
                            if q_id in model_q_map:
                                q["nota_maxima"] = model_q_map[q_id].get("nota_maxima", 10.0)

                        # Avalia com a IA
                        resultado_aluno = exam_correction_service.correct_exam(ocr_data)
                        resultado_aluno["prova_modelo_id"] = selected_prova_modelo.get("prova_id")
                        resultado_aluno["prova_titulo"] = selected_prova_modelo.get("titulo", "Prova")
                        resultado_aluno["arquivo_origem"] = file_obj.name

                        resultados_turma.append(resultado_aluno)
                    except Exception as e:
                        st.error(f"Erro ao processar arquivo {file_obj.name}: {e}")
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

                status_text.success(f"✅ Processamento de {len(resultados_turma)} alunos concluído com sucesso!")
                st.session_state["turma_resultados"] = resultados_turma
                st.rerun()

with tab_json:
    st.subheader("📄 Upload de Respostas da Turma em JSON")
    json_file = st.file_uploader(
        "Selecione um arquivo .json contendo a lista de alunos e suas respostas",
        type=["json"]
    )

    if json_file:
        try:
            turma_input_data = json.load(json_file)
            if isinstance(turma_input_data, dict) and "alunos" in turma_input_data:
                turma_input_data = turma_input_data["alunos"]

            if not isinstance(turma_input_data, list):
                st.error("O JSON enviado deve ser uma lista de alunos (ou um objeto com a chave 'alunos').")
            else:
                st.write(f"📄 **{len(turma_input_data)} alunos identificados no arquivo JSON.**")
                st.json(turma_input_data[:2])  # Preview dos primeiros 2

                if st.button("🤖 Avaliar Turma com IA", type="primary", use_container_width=True, key="btn_eval_json"):
                    progress_bar = st.progress(0.0)
                    status_text = st.empty()

                    def update_progress(current, total, nome_aluno):
                        status_text.markdown(f"⏳ **Avaliando Aluno {current} de {total}**: {nome_aluno}...")
                        progress_bar.progress(current / total)

                    resultados_turma = exam_correction_service.correct_batch_json(
                        turma_input_data,
                        prova_modelo=selected_prova_modelo,
                        progress_callback=update_progress
                    )

                    status_text.success(f"✅ Avaliação em lote de {len(resultados_turma)} alunos concluída!")
                    st.session_state["turma_resultados"] = resultados_turma
                    st.rerun()
        except Exception as e:
            st.error(f"Erro ao ler arquivo JSON: {e}")

# ======================================================
# 3. Painel Geral da Turma e Revisão Individual
# ======================================================

turma_resultados = st.session_state.get("turma_resultados")

if turma_resultados:
    st.divider()
    st.header("📊 Painel Consolidado da Turma")

    notas_finais = [item["nota_final"] for item in turma_resultados]
    media_turma = sum(notas_finais) / len(notas_finais) if notas_finais else 0.0
    maior_nota = max(notas_finais) if notas_finais else 0.0
    menor_nota = min(notas_finais) if notas_finais else 0.0

    # Cards com métricas principais da turma
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Média da Turma", f"{media_turma:.2f}")
    c2.metric("Maior Nota", f"{maior_nota:.2f}")
    c3.metric("Menor Nota", f"{menor_nota:.2f}")
    c4.metric("Total de Alunos", len(turma_resultados))

    st.subheader("📋 Tabela Resumo das Notas")
    tabela_resumo = [
        {
            "Aluno": item["aluno"],
            "Prova": item.get("prova_titulo", "N/A"),
            "Nota Final Obteve": f"{item['nota_final']:.2f}",
            "Qtd Questões": len(item.get("questoes", [])),
            "Arquivo Origem": item.get("arquivo_origem", "JSON/Digitado")
        }
        for item in turma_resultados
    ]
    st.dataframe(tabela_resumo, use_container_width=True)

    st.divider()
    st.subheader("🔍 Revisão Individual dos Alunos (Human-in-the-Loop)")
    st.info("Expanda cada aluno para conferir o texto extraído, as justificativas da IA e ajustar as notas finais se necessário.")

    resultados_editados_turma = []

    for aluno_idx, aluno_res in enumerate(turma_resultados):
        aluno_nome_label = f"👤 {aluno_res['aluno']} — Nota Sugerida: {aluno_res['nota_final']:.2f}"

        with st.expander(aluno_nome_label, expanded=False):
            aluno_nome_edit = st.text_input(
                "Nome do Aluno",
                value=aluno_res["aluno"],
                key=f"nome_aluno_{aluno_idx}"
            )

            questoes_finais_aluno = []
            nota_total_editada = 0.0

            for q_idx, q_eval in enumerate(aluno_res["questoes"]):
                st.markdown(f"#### Questão ID {q_eval['questao_id']}")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Nota Sugerida pela IA", f"{q_eval['nota']} / {q_eval.get('nota_maxima', 10.0)}")
                with col_b:
                    st.metric("Confiança da IA", f"{q_eval.get('confianca', 1.0):.1%}")

                st.write("**Resposta Extraída do Aluno:**")
                resp_aluno_text = st.text_area(
                    "Resposta do Aluno",
                    value=q_eval["resposta_aluno"],
                    key=f"resp_t_{aluno_idx}_{q_idx}"
                )

                st.write("**Justificativa da IA:**")
                st.write(q_eval["justificativa"])

                # Respostas RAG
                if q_eval.get("exemplos"):
                    with st.expander("Precedentes Históricos (RAG)"):
                        for ex in q_eval["exemplos"]:
                            st.write(f"• **Exemplo:** {ex['resposta']} | **Nota:** {ex['nota']} | **Feedback:** {ex['feedback']}")

                n_final = st.number_input(
                    f"Nota Final (Questão ID {q_eval['questao_id']})",
                    min_value=0.0,
                    max_value=float(q_eval.get("nota_maxima", 10.0)),
                    value=float(q_eval["nota"]),
                    step=0.5,
                    key=f"nota_t_{aluno_idx}_{q_idx}"
                )

                fb_final = st.text_area(
                    f"Feedback Final (Questão ID {q_eval['questao_id']})",
                    value=q_eval["justificativa"],
                    key=f"fb_t_{aluno_idx}_{q_idx}"
                )

                nota_total_editada += n_final

                questoes_finais_aluno.append({
                    "questao_id": q_eval["questao_id"],
                    "resposta_aluno": resp_aluno_text,
                    "nota": n_final,
                    "feedback": fb_final,
                    "confianca": q_eval.get("confianca", 1.0),
                    "origem": "manual" if (n_final != q_eval["nota"] or fb_final != q_eval["justificativa"]) else "automatica"
                })
                st.markdown("---")

            resultados_editados_turma.append({
                "aluno": aluno_nome_edit,
                "prova_modelo_id": aluno_res.get("prova_modelo_id"),
                "prova_titulo": aluno_res.get("prova_titulo", "Prova"),
                "nota_final": nota_total_editada,
                "questoes": questoes_finais_aluno
            })

    st.markdown("---")
    st.subheader("💾 Ações em Lote para a Turma")

    col_save_batch, col_dl_json, col_dl_csv = st.columns(3)

    with col_save_batch:
        if st.button("💾 Salvar TODAS as Correções no Histórico e RAG", type="primary", use_container_width=True):
            for aluno_doc in resultados_editados_turma:
                # Grava no ExamRepository
                prova_record = {
                    "prova_id": len(exam_repository.get_all()) + 1,
                    "prova_modelo_id": aluno_doc.get("prova_modelo_id"),
                    "prova_titulo": aluno_doc.get("prova_titulo"),
                    "aluno": aluno_doc["aluno"],
                    "nota_final": aluno_doc["nota_final"],
                    "questoes": aluno_doc["questoes"]
                }
                exam_repository.add(prova_record)

                # Grava no histórico individual e na base vetorial RAG
                for qf in aluno_doc["questoes"]:
                    correction_service.save_manual_correction(
                        questao_id=qf["questao_id"],
                        resposta_aluno=qf["resposta_aluno"],
                        nota=qf["nota"],
                        feedback=qf["feedback"],
                        aluno=aluno_doc["aluno"]
                    )

            st.success(f"✅ {len(resultados_editados_turma)} provas salvas com sucesso no Histórico e RAG!")
            del st.session_state["turma_resultados"]
            st.rerun()

    with col_dl_json:
        json_turma_export = json.dumps(resultados_editados_turma, ensure_ascii=False, indent=4)
        st.download_button(
            label="⬇️ Baixar JSON da Turma",
            data=json_turma_export,
            file_name="correcao_turma.json",
            mime="application/json",
            use_container_width=True
        )

    with col_dl_csv:
        csv_turma_export = exam_correction_service.export_batch_summary_csv(resultados_editados_turma)
        st.download_button(
            label="⬇️ Baixar Relatório CSV",
            data=csv_turma_export,
            file_name="relatorio_turma_notas.csv",
            mime="text/csv",
            use_container_width=True
        )
