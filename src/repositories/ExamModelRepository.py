import json
from config import EXAM_MODELS_FILE


class ExamModelRepository:

    def __init__(self):
        self.file_path = EXAM_MODELS_FILE

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_all(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_by_id(self, prova_id):
        provas = self.get_all()
        for prova in provas:
            if prova.get("prova_id") == prova_id:
                return prova
        return None

    def add(self, prova):
        provas = self.get_all()
        provas.append(prova)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(provas, f, ensure_ascii=False, indent=4)

    def update(self, prova_atualizada):
        provas = self.get_all()
        for i, p in enumerate(provas):
            if p.get("prova_id") == prova_atualizada.get("prova_id"):
                provas[i] = prova_atualizada
                break
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(provas, f, ensure_ascii=False, indent=4)

    def delete(self, prova_id):
        provas = self.get_all()
        provas = [p for p in provas if p.get("prova_id") != prova_id]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(provas, f, ensure_ascii=False, indent=4)
