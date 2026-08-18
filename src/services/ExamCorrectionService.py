import csv
import io
import json


class ExamCorrectionService:

    def __init__(self, correction_service):
        self.correction_service = correction_service

    def correct_exam(self, prova):
        """Avalia uma única prova contendo a lista de questões e respostas do aluno."""
        nota_total = 0
        questoes_avaliadas = []

        for questao in prova.get("questoes", []):
            q_id = questao["questao_id"]
            resp_aluno = questao.get("resposta_aluno", "")
            nota_maxima = questao.get("nota_maxima", 10.0)

            resultado = self.correction_service.correct(q_id, resp_aluno)

            questoes_avaliadas.append({
                "questao_id": q_id,
                "resposta_aluno": resp_aluno,
                "nota": resultado["nota"],
                "nota_maxima": nota_maxima,
                "justificativa": resultado["justificativa"],
                "confianca": resultado["confianca"],
                "exemplos": resultado.get("exemplos", []),
                "origem": "automatica"
            })
            nota_total += resultado["nota"]

        return {
            "aluno": prova.get("aluno", "Aluno Desconhecido"),
            "prova_modelo_id": prova.get("prova_modelo_id"),
            "prova_titulo": prova.get("prova_titulo", "Prova"),
            "nota_final": nota_total,
            "questoes": questoes_avaliadas
        }

    def correct_batch_json(self, turma_data, prova_modelo=None, progress_callback=None):
        """
        Avalia um conjunto (lote) de provas no formato JSON/Lista.
        turma_data: list of dicts, ex: [{"aluno": "Nome", "questoes": [{"questao_id": 1, "resposta_aluno": "..."}, ...]}, ...]
        """
        resultados = []
        total_alunos = len(turma_data)

        for idx, aluno_doc in enumerate(turma_data, start=1):
            if progress_callback:
                progress_callback(idx, total_alunos, aluno_doc.get("aluno", f"Aluno {idx}"))

            # Se houver prova_modelo, injeta nota_maxima para cada questão se não estiver presente
            if prova_modelo and "questoes" in prova_modelo:
                model_q_map = {q["questao_id"]: q for q in prova_modelo["questoes"]}
                for q in aluno_doc.get("questoes", []):
                    q_id = q.get("questao_id")
                    if q_id in model_q_map and "nota_maxima" not in q:
                        q["nota_maxima"] = model_q_map[q_id].get("nota_maxima", 10.0)

            resultado_aluno = self.correct_exam(aluno_doc)
            if prova_modelo:
                resultado_aluno["prova_modelo_id"] = prova_modelo.get("prova_id")
                resultado_aluno["prova_titulo"] = prova_modelo.get("titulo", "Prova")

            resultados.append(resultado_aluno)

        return resultados

    def export_batch_summary_csv(self, resultados_turma):
        """Gera uma string no formato CSV com o resumo das notas da turma."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Aluno", "Prova/Modelo", "Nota Final", "Qtd Questões", "Confiança Média"])

        for item in resultados_turma:
            aluno = item.get("aluno", "N/A")
            prova_titulo = item.get("prova_titulo", "N/A")
            nota_final = item.get("nota_final", 0.0)
            questoes = item.get("questoes", [])
            qtd_q = len(questoes)
            conf_media = (sum(q.get("confianca", 0.0) for q in questoes) / qtd_q) if qtd_q > 0 else 0.0

            writer.writerow([aluno, prova_titulo, f"{nota_final:.2f}", qtd_q, f"{conf_media:.2%}"])

        return output.getvalue()