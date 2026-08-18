import streamlit as st

st.set_page_config(
    page_title="Correção Assistida por IA",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Sistema de Correção Assistida por IA")

st.markdown("""
Seja bem-vindo ao **Sistema de Correção Assistida por IA**, uma plataforma desenvolvida para otimizar, agilizar e padronizar o processo de avaliação de questões discursivas e provas escritas.
""")

st.divider()

# Destaques das funcionalidades em colunas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("### 📚 1. Cadastro\nCadastre questões com gabaritos oficiais, critérios detalhados e pontuação máxima.")

with col2:
    st.success("### 🤖 2. IA + RAG\nAvaliação inteligente baseada na resposta modelo e em correções anteriores (RAG).")

with col3:
    st.warning("### 📷 3. OCR Provas\nExtração automática de respostas a partir de fotos/imagens de provas físicas.")

with col4:
    st.error("### 👤 4. Human-in-the-Loop\nO professor mantém o controle total para revisar, ajustar e confirmar a nota final.")

st.divider()

st.subheader("📖 Como Usar o Aplicativo (Guia Passo a Passo)")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1️⃣ Cadastrar Questões",
    "2️⃣ Criar Prova (JSON)",
    "3️⃣ Correção por Texto",
    "4️⃣ Correção por OCR (Imagem)",
    "5️⃣ Aprendizado Contínuo (RAG)",
    "6️⃣ Histórico"
])


with tab1:
    st.markdown("""
    ### 📚 Passo 1: Cadastrar a Questão
    Antes de iniciar as correções, você deve cadastrar as questões no banco do sistema.
    
    1. Acesse a página **`Cadastro de Questões`** (`questoes`) no menu lateral.
    2. Preencha o **Enunciado** da questão.
    3. Forneça a **Resposta Modelo (Gabarito)** contendo os pontos essenciais esperados.
    4. Defina os **Critérios de Avaliação** (exemplo: *Atribuir 2 pontos se explicar o conceito X; 3 pontos se der exemplo prático*).
    5. Defina a **Nota Máxima** e clique em **Salvar**.
    """)

with tab2:
    st.markdown("""
    ### 📝 Passo 2: Montar e Exportar Prova (JSON)
    Crie provas personalizadas selecionando questões do repositório cadastrado.
    
    1. Acesse a página **`Criador de Provas`** (`criar_prova`) no menu lateral.
    2. Informe o **Título da Prova** e a **Disciplina**.
    3. Selecione as questões desejadas na lista suspensa.
    4. Ajuste a nota máxima de cada questão se necessário.
    5. Clique em **💾 Salvar Prova no Sistema** para guardar a estrutura em `provas_modelo.json`.
    6. Clique em **⬇️ Baixar JSON da Prova** para exportar o arquivo `.json` gerado.
    """)

with tab3:
    st.markdown("""
    ### 📝 Passo 3A: Correção Individual por Texto
    Recomendado para respostas digitadas diretamente pelos alunos ou copiadas de formulários digitais.
    
    1. Acesse a página **`Correção de Questões`** (`correcao`) no menu lateral.
    2. Selecione a questão cadastrada no menu suspenso.
    3. Cole ou digite a **Resposta do Aluno** na caixa de texto.
    4. Clique no botão **Corrigir**.
    5. O sistema exibirá a análise da IA:
       - **Nota sugerida** e **Nível de Confiança** da avaliação.
       - **Justificativa pedagógica** detalhada com base nos critérios.
       - **Respostas similares históricas** encontradas no banco (RAG) para comparação.
    6. **Revisão Final:** Você pode ajustar a nota ou editar o feedback se desejar, e depois clicar em **Salvar correção**.
    """)

with tab4:
    st.markdown("""
    ### 📷 Passo 3B: Correção de Prova por Imagem (OCR)
    Recomendado para provas físicas manuscritas ou impressas digitalizadas por foto.
    
    1. Acesse a página **`Correção de Prova por Imagem (OCR)`** (`upload_prova`) no menu lateral.
    2. Faça o upload da imagem da prova (`.png`, `.jpg`, `.jpeg`).
    3. Clique em **🔍 Extrair Texto (OCR)**.
    4. **Revisão Humana (Human-in-the-Loop):**
       - Verifique o nome do aluno identificado pela IA.
       - Confira as respostas extraídas para cada questão e corrija eventuais erros de leitura do OCR.
    5. Clique em **🤖 Avaliar Prova com IA**.
    6. Analise a nota geral, as justificativas e as sugestões da IA por questão.
    7. Ajuste as notas finais e feedbacks se necessário.
    8. Clique em **💾 Salvar Correções no Histórico e RAG** para salvar o resultado da prova inteira.
    """)

with tab5:
    st.markdown("""
    ### 🧠 Como Funciona o Aprendizado Contínuo (RAG)?
    O sistema utiliza a tecnologia **RAG (Retrieval-Augmented Generation)** com busca por similaridade vetorial:
    
    - Sempre que o professor salva uma correção, ela se torna um **precedente de avaliação**.
    - Ao avaliar novas respostas, a IA pesquisa no histórico as respostas **semanticamente mais parecidas**.
    - Essa busca por precedentes garante **maior isonomia, padronização e coerência** nas notas atribuídas a diferentes alunos.
    - Quanto mais você utiliza e confirma correções, mais o sistema se adapta aos critérios de avaliação da sua instituição!
    """)

with tab6:
    st.markdown("""
    ### 📊 Passo 4: Consultar o Histórico de Correções
    
    1. Acesse a página **`Histórico`** (`historico`) no menu lateral.
    2. Consulte a lista de todas as correções efetuadas até o momento.
    3. Acompanhe os registros de notas, respostas e feedbacks concedidos.
    """)


st.divider()

st.subheader("💡 Dicas para Obter os Melhores Resultados")

st.info("""
- **Critérios detalhados:** Quanto mais específicos forem os critérios de pontuação no cadastro da questão, mais precisa e detalhada será a justificativa da IA.
- **Qualidade da Foto (OCR):** Para provas físicas, utilize boa iluminação e foco limpo no texto manuscrito/impresso para maximizar a precisão do OCR.
- **Sempre revise:** A IA atua como uma assistente pedagógica. A validação e decisão final cabem sempre ao professor.
""")

st.sidebar.markdown("---")
st.sidebar.info("👈 Utilize o menu lateral acima para navegar entre as seções do aplicativo.")
