import json
import uuid
from datetime import date


class ExamModelService:

    def __init__(self, exam_model_repository, question_repository):
        self.exam_model_repository = exam_model_repository
        self.question_repository = question_repository

    def list_exam_models(self):
        return self.exam_model_repository.get_all()

    def get_exam_model(self, prova_id):
        return self.exam_model_repository.get_by_id(prova_id)

    def create_exam_model(self, titulo, disciplina, me_questoes, instrucoes=""):
        if not titulo or not str(titulo).strip():
            raise ValueError("O título da prova é obrigatório.")
        
        if not me_questoes:
            raise ValueError("A prova deve conter pelo menos uma questão.")

        # Monta a lista de questões com número sequencial e notas
        questoes_formatadas = []
        nota_total = 0.0

        for idx, item in enumerate(me_questoes, start=1):
            q_id = item["questao_id"]
            nota_maxima = float(item.get("nota_maxima", 10.0))
            
            # Busca do repositório de questões se necessário
            q_original = self.question_repository.get_by_id(q_id)
            if not q_original:
                continue

            questoes_formatadas.append({
                "numero": idx,
                "questao_id": q_id,
                "enunciado": q_original.get("enunciado", ""),
                "resposta_modelo": q_original.get("resposta_modelo", ""),
                "criterios": q_original.get("criterios", ""),
                "nota_maxima": nota_maxima
            })
            nota_total += nota_maxima

        # Gerar um ID amigável ou UUID
        slug_titulo = titulo.lower().replace(" ", "_")[:20]
        prova_id = f"prova_{slug_titulo}_{uuid.uuid4().hex[:6]}"

        nova_prova = {
            "prova_id": prova_id,
            "titulo": titulo.strip(),
            "disciplina": disciplina.strip() if disciplina else "Geral",
            "instrucoes": instrucoes.strip() if instrucoes else "",
            "data_criacao": str(date.today()),
            "nota_total_maxima": nota_total,
            "questoes": questoes_formatadas
        }

        self.exam_model_repository.add(nova_prova)
        return nova_prova

    def delete_exam_model(self, prova_id):
        self.exam_model_repository.delete(prova_id)

    def export_json_string(self, prova_dict):
        return json.dumps(prova_dict, ensure_ascii=False, indent=4)
