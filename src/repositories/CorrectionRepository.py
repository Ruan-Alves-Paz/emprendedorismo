import json
import os
from config import DATA_DIR


class CorrectionRepository:

    def __init__(self, file_path=DATA_DIR / "correcoes.json"):
        self.file_path = file_path

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_all(self):

        if not self.file_path.exists():
            return []

        try:

            with self.file_path.open(
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except json.JSONDecodeError:

            return []

    def get_by_question(self, questao_id):
        correcoes = self.get_all()

        return [
            c for c in correcoes
            if c["questao_id"] == questao_id
        ]

    def add(self, correcao):
        if not correcao.get("aluno") or not str(correcao["aluno"]).strip():
            raise ValueError("O nome do aluno é obrigatório para registrar a correção.")

        correcoes = self.get_all()

        if len(correcoes) == 0:
            novo_id = 1
        else:
            novo_id = max(c["id"] for c in correcoes) + 1

        correcao["id"] = novo_id

        correcoes.append(correcao)

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(correcoes, f, ensure_ascii=False, indent=4)

    def update(self, correcao):

        correcoes = self.get_all()

        for i, c in enumerate(correcoes):
            if c["id"] == correcao["id"]:
                correcoes[i] = correcao
                break

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(correcoes, f, ensure_ascii=False, indent=4)