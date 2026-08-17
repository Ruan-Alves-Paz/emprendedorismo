class CorrectionService:

    def __init__(
        self,
        question_repository,
        correction_repository,
        retriever,
        evaluator
    ):

        self.question_repository = question_repository
        self.correction_repository = correction_repository
        self.retriever = retriever
        self.evaluator = evaluator
        
    def correct(self, questao_id, resposta_aluno):

        questao = self.question_repository.get_by_id(
            questao_id
        )

        exemplos = self.retriever.search(
            questao_id,
            resposta_aluno
        )

        resultado = self.evaluator.evaluate(
            questao["enunciado"],
            questao["resposta_modelo"],
            resposta_aluno,
            questao["criterios"],
            exemplos
        )
        
        resultado["exemplos"] = exemplos

        return resultado
    
    def save_manual_correction(self, questao_id, resposta_aluno, nota, feedback):

        correcao = {
            "questao_id": questao_id,
            "resposta_aluno": resposta_aluno,
            "nota": nota,
            "feedback": feedback,
            "origem": "manual"
        }

        # Salva no histórico
        self.correction_repository.add(correcao)

        # Adiciona ao banco vetorial
        self.retriever.add(
            questao_id=questao_id,
            resposta=resposta_aluno,
            nota=nota,
            feedback=feedback
        )

        
    def save_automatic_correction(self, questao_id, resposta_aluno, resultado):

        correcao = {
            "questao_id": questao_id,
            "resposta_aluno": resposta_aluno,
            "nota": resultado["nota"],
            "feedback": resultado["justificativa"],
            "origem": "automatica",
        }

        self.correction_repository.add(correcao)
        