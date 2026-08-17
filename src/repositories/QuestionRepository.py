import json
import os
from config import DATA_DIR


class QuestionRepository:

    def __init__(self, file_path=DATA_DIR / "questoes.json"):
        self.file_path = file_path

        # Cria o arquivo caso não exista
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_all(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_by_id(self, questao_id):
        questoes = self.get_all()

        for questao in questoes:
            if questao["questao_id"] == questao_id:
                return questao

        return None
    
    def get_by_enunciado(self, enunciado):
        questoes = self.get_all()

        for questao in questoes:
            if questao["enunciado"] == enunciado:
                return questao

        return None

    def add(self, questao):
        questoes = self.get_all()

        questoes.append(questao)

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(questoes, f, ensure_ascii=False, indent=4)

    def update(self, questao_atualizada):
        questoes = self.get_all()

        for i, questao in enumerate(questoes):
            if questao["questao_id"] == questao_atualizada["questao_id"]:
                questoes[i] = questao_atualizada
                break

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(questoes, f, ensure_ascii=False, indent=4)

    def delete(self, questao_id):
        questoes = self.get_all()

        questoes = [
            q for q in questoes
            if q["questao_id"] != questao_id
        ]

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(questoes, f, ensure_ascii=False, indent=4)