class ExamCorrectionService:

    def __init__(self, correction_service):
        self.correction_service = correction_service

    def correct_exam(self, prova):

        nota_final = 0

        for questao in prova["questoes"]:

            resultado = self.correction_service.correct(
                questao["questao_id"],
                questao["resposta_aluno"]
            )

            questao["correcao"] = {
                "nota": resultado["nota"],
                "feedback": resultado["justificativa"],
                "confianca": resultado["confianca"],
                "origem": "automatica"
            }

            nota_final += resultado["nota"]

        prova["nota_final"] = nota_final/len(prova["questoes"]) if len(prova["questoes"]) > 0 else 0

        return prova