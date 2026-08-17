import json
import ollama


class OCRExtractor:

    def __init__(self, model="qwen2.5vl:3b"):
        self.model = model

    def extract(self, image_path):

        response = ollama.chat(
            model=self.model,
            format="json",
            messages=[
                {
                    "role": "system",
                    "content": """
Você é um sistema de OCR especializado em provas discursivas.

Sua única função é extrair informações da imagem.

NÃO avalie respostas.
NÃO corrija respostas.
NÃO complete frases.
NÃO interprete textos.
NÃO reescreva respostas.
NÃO invente informações.

Copie exatamente o que estiver escrito pelo aluno.

Caso algum trecho esteja ilegível, mantenha o restante da resposta e utilize "[ilegível]" apenas naquele trecho.

Retorne SOMENTE um JSON válido.
...
"""
                },
                {
                    "role": "user",
                    "content": """
Extraia da prova:

1. Nome do aluno.

2. Para cada questão:
   - número da questão (questao_id);
   - resposta escrita pelo aluno.

Ignore:
- enunciados;
- figuras;
- cabeçalhos;
- rodapés;
- notas do professor;
- rasuras que não façam parte da resposta.

Retorne exatamente neste formato:

{
    "aluno": "Nome do aluno",
    "questoes": [
        {
            "questao_id": 1,
            "resposta_aluno": "texto exatamente como escrito pelo aluno"
        }
    ]
}
...
""",
                    "images": [image_path]
                }
            ]
        )

        return json.loads(
            response["message"]["content"]
        )