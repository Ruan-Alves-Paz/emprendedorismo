# Sistema Inteligente de Correção de Questões Discursivas

Sistema de correção semiautomática de questões discursivas utilizando **Large Language Models (LLMs)**, **Retrieval-Augmented Generation (RAG)** e **Human-in-the-Loop (HITL)** para aumentar a consistência das avaliações.

## Objetivo

O projeto busca auxiliar professores na correção de questões discursivas, fornecendo uma nota sugerida, justificativa da avaliação e exemplos de respostas semelhantes previamente corrigidas.

Ao contrário de um corretor baseado apenas em LLM, o sistema aprende gradualmente o padrão de correção do professor por meio das avaliações realizadas manualmente.

---

## Principais funcionalidades

- Cadastro de disciplinas e questões.
- Cadastro de resposta modelo.
- Definição de critérios de avaliação para cada questão.
- Extração de texto de imagens de provas via OCR (Qwen2.5-VL).
- Correção automática utilizando LLM.
- Recuperação de respostas semelhantes previamente corrigidas (RAG).
- Correção manual pelo professor.
- Aprendizado incremental a partir das correções humanas.
- Histórico de correções.
- Interface web desenvolvida com Streamlit.

---

## Arquitetura

```text
Resposta do aluno (Texto / OCR da imagem)
        │
        ▼
Busca da questão
        │
        ▼
Retriever (ChromaDB)
        │
        ▼
Respostas semelhantes
        │
        ▼
LLM (Gemma)
        │
        ▼
Nota + Justificativa
        │
        ▼
Professor revisa
        │
        ▼
Correção armazenada
        │
        ▼
Base vetorial atualizada
```

---

## Tecnologias utilizadas

- Python
- Streamlit
- Ollama
- Gemma
- Qwen2.5-VL (OCR)
- ChromaDB
- JSON (persistência local)

---

## Estrutura do projeto

```text
emprendedorismo/

├── data/
│   ├── questoes.json
│   ├── correcoes.json
│   └── prova.json
│
├── src/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── retriever.py
│   ├── evaluator.py
│   ├── ocr.py
│   ├── dependecies.py
│   │
│   ├── pages/
│   │   ├── questoes.py
│   │   ├── correcao.py
│   │   ├── upload_prova.py
│   │   └── historico.py
│   │
│   ├── repositories/
│   ├── services/
│   └── ...
│
└── vector_database/
```

---

## Funcionamento

### 1. Cadastro da questão

Cada questão possui:

- Disciplina
- Enunciado
- Resposta modelo
- Critérios de avaliação
- Nota máxima

### 2. Correção

Ao receber uma resposta do aluno (digitada ou extraída via OCR), o sistema:

1. Recupera a questão correspondente.
2. Busca respostas semanticamente semelhantes no ChromaDB.
3. Envia para a LLM:
   - Enunciado;
   - Resposta modelo;
   - Critérios de avaliação;
   - Resposta do aluno;
   - Exemplos recuperados.
4. Recebe:
   - Nota sugerida;
   - Justificativa;
   - Confiança da avaliação.

### 3. Revisão do professor

O professor pode:

- Aceitar a correção automática.
- Alterar a nota sugerida.
- Alterar o feedback.

Quando ocorre uma correção manual, ela é armazenada tanto no histórico quanto na base vetorial.

### 4. Aprendizado incremental

Cada nova correção manual passa a fazer parte da base de exemplos.

Nas próximas avaliações, respostas semelhantes poderão ser recuperadas e utilizadas como referência pela LLM, promovendo maior consistência nas notas atribuídas.

---

## Human-in-the-Loop

O sistema adota uma abordagem **Human-in-the-Loop**, em que o professor permanece responsável pela decisão final.

As correções humanas alimentam continuamente a base de conhecimento utilizada pelo sistema.

Essa estratégia reduz inconsistências e adapta a IA ao padrão de correção de cada professor.

---

## RAG aplicado à correção

Diferentemente de aplicações tradicionais de RAG, o sistema não recupera apenas conteúdo didático.

Ele recupera **precedentes de avaliação**, ou seja, respostas anteriormente corrigidas juntamente com suas notas e feedbacks.

Assim, a LLM consegue manter maior consistência entre respostas semanticamente semelhantes.

---

## Executando o projeto

### Clone o repositório

```bash
git clone <url-do-repositorio>
cd emprendedorismo
```

### Instale as dependências

```bash
pip install -r requirements.txt
```

### Instale os modelos no Ollama

```bash
ollama pull gemma4
ollama pull qwen2.5vl:3b
```

> Substitua `gemma4` ou `qwen2.5vl:3b` pelos modelos desejados, caso utilize outros.

### Execute a aplicação

```bash
streamlit run src/app.py
```

---

## Trabalhos futuros

- Correção automática de provas completas.
- Suporte a múltiplos professores.
- Suporte a múltiplas disciplinas.
- Reranking das respostas recuperadas.
- Benchmark entre diferentes LLMs.
- Avaliação quantitativa da consistência das correções.
- Dashboard com métricas de desempenho.
- Exportação das correções para PDF e planilhas.

---

## Licença

Este projeto foi desenvolvido para fins acadêmicos e de pesquisa.
