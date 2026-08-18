import json
import streamlit as st

from dependecies import question_service, exam_model_service

st.set_page_config(page_title="Criador de Provas", page_icon="📝", layout="wide")

st.title("📝 Criador de Provas")
st.markdown("""
Crie gabaritos e estruturas de provas personalizadas contendo as questões cadastradas no sistema.
O sistema gera um arquivo **JSON** padronizado que pode ser baixado ou armazenado para aplicação e correção.
""")

tab_criar, tab_lista = st.tabs(["📝 Nova Prova", "📚 Provas Criadas"])

# ======================================================
# TAB 1: CRIAR NOVA PROVA
# ======================================================
with tab_criar:
    questoes_disponiveis = question_service.list_questions()

    if not questoes_disponiveis:
        st.warning("⚠️ Nenhuma questão cadastrada. Cadastre questões na página **Cadastro de Questões** antes de criar uma prova.")
    else:
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            titulo = st.text_input(
                "Título da Prova",
                placeholder="Ex: Avaliação P1 - Programação Orientada a Objetos"
            )
        with col_meta2:
            disciplina = st.text_input(
                "Disciplina",
                placeholder="Ex: POO / Engenharia de Software"
            )

        instrucoes = st.text_area(
            "Instruções da Prova (Opcional)",
            placeholder="Ex: Leia atentamente cada questão. Responda de forma clara e objetiva.",
            height=100
        )

        st.subheader("📌 Seleção de Questões")
        st.write("Selecione as questões que farão parte desta prova:")

        # Mapeamento para o multiselect
        options_map = {
            f"ID {q['questao_id']} - {q['enunciado'][:70]}...": q['questao_id']
            for q in questoes_disponiveis
        }

        selected_labels = st.multiselect(
            "Escolha as questões",
            options=list(options_map.keys()),
            help="Selecione uma ou mais questões para compor a prova"
        )

        selected_ids = [options_map[lbl] for lbl in selected_labels]

        questoes_selecionadas_dados = []
        nota_total_preview = 0.0

        if selected_ids:
            st.markdown("---")
            st.subheader("⚙️ Configurar Pontuação das Questões Selecionadas")

            for idx, q_id in enumerate(selected_ids, start=1):
                q = next(item for item in questoes_disponiveis if item["questao_id"] == q_id)
                
                with st.expander(f"Questão {idx} (ID {q_id}): {q['enunciado'][:60]}...", expanded=True):
                    st.write(f"**Enunciado:** {q['enunciado']}")
                    st.write(f"**Resposta Modelo:** {q['resposta_modelo']}")
                    if q.get("criterios"):
                        st.caption(f"**Critérios:** {q['criterios']}")

                    nota_max = st.number_input(
                        f"Nota Máxima (Questão {idx})",
                        min_value=0.5,
                        max_value=100.0,
                        value=float(q.get("nota_maxima", 10.0)),
                        step=0.5,
                        key=f"nota_q_{q_id}_{idx}"
                    )

                    questoes_selecionadas_dados.append({
                        "questao_id": q_id,
                        "nota_maxima": nota_max
                    })
                    nota_total_preview += nota_max

            st.info(f"📊 **Nota Total da Prova:** {nota_total_preview:.1f} pontos")

            # Montagem do JSON Preview
            prova_preview = {
                "prova_id": "preview_id",
                "titulo": titulo if titulo else "Sem Título",
                "disciplina": disciplina if disciplina else "Geral",
                "instrucoes": instrucoes,
                "nota_total_maxima": nota_total_preview,
                "questoes": [
                    {
                        "numero": idx + 1,
                        "questao_id": item["questao_id"],
                        "enunciado": next(q["enunciado"] for q in questoes_disponiveis if q["questao_id"] == item["questao_id"]),
                        "resposta_modelo": next(q["resposta_modelo"] for q in questoes_disponiveis if q["questao_id"] == item["questao_id"]),
                        "criterios": next(q.get("criterios", "") for q in questoes_disponiveis if q["questao_id"] == item["questao_id"]),
                        "nota_maxima": item["nota_maxima"]
                    }
                    for idx, item in enumerate(questoes_selecionadas_dados)
                ]
            }

            st.markdown("---")
            st.subheader("📄 Pré-visualização do JSON Gerado")
            json_preview_str = json.dumps(prova_preview, ensure_ascii=False, indent=4)
            st.json(prova_preview)

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("💾 Salvar Prova no Sistema", use_container_width=True, type="primary"):
                    try:
                        prova_criada = exam_model_service.create_exam_model(
                            titulo=titulo,
                            disciplina=disciplina,
                            me_questoes=questoes_selecionadas_dados,
                            instrucoes=instrucoes
                        )
                        st.success(f"✅ Prova '{prova_criada['titulo']}' criada e salva com sucesso (ID: {prova_criada['prova_id']})!")
                        st.rerun()
                    except ValueError as ve:
                        st.error(f"⚠️ {ve}")
                    except Exception as e:
                        st.error(f"Erro ao salvar prova: {e}")

            with col_btn2:
                file_name = f"prova_{(titulo or 'modelo').lower().replace(' ', '_')}.json"
                st.download_button(
                    label="⬇️ Baixar JSON da Prova",
                    data=json_preview_str,
                    file_name=file_name,
                    mime="application/json",
                    use_container_width=True
                )

# ======================================================
# TAB 2: PROVAS CRIADAS
# ======================================================
with tab_lista:
    provas_existentes = exam_model_service.list_exam_models()

    if not provas_existentes:
        st.info("Nenhuma prova foi criada ainda.")
    else:
        st.write(f"Total de provas cadastradas: **{len(provas_existentes)}**")

        for p in provas_existentes:
            with st.expander(f"📝 {p.get('titulo', 'Sem Título')} ({p.get('disciplina', 'Geral')}) - ID: {p.get('prova_id')}"):
                st.write(f"**Data de Criação:** {p.get('data_criacao', 'N/A')}")
                st.write(f"**Nota Total Máxima:** {p.get('nota_total_maxima', 0.0)}")
                if p.get("instrucoes"):
                    st.write(f"**Instruções:** {p.get('instrucoes')}")

                st.write(f"**Quantidade de Questões:** {len(p.get('questoes', []))}")

                json_str = exam_model_service.export_json_string(p)

                col_dl, col_del = st.columns([3, 1])

                with col_dl:
                    file_name = f"{p.get('prova_id', 'prova')}.json"
                    st.download_button(
                        label=f"⬇️ Baixar JSON ({file_name})",
                        data=json_str,
                        file_name=file_name,
                        mime="application/json",
                        key=f"dl_{p['prova_id']}"
                    )

                with col_del:
                    if st.button("🗑️ Excluir", key=f"del_{p['prova_id']}"):
                        exam_model_service.delete_exam_model(p['prova_id'])
                        st.success(f"Prova {p['prova_id']} excluída!")
                        st.rerun()

                st.json(p)
