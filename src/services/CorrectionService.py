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
            questao.get("nota_maxima", 10),
            exemplos
        )
        
        resultado["exemplos"] = exemplos

        return resultado
    
    def save_manual_correction(self, questao_id, resposta_aluno, nota, feedback, aluno):
        if not aluno or not str(aluno).strip():
            raise ValueError("O nome do aluno é obrigatório para salvar a correção.")

        correcao = {
            "questao_id": questao_id,
            "aluno": aluno.strip(),
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
            feedback=feedback,
            aluno=aluno.strip()
        )

    def save_automatic_correction(self, questao_id, resposta_aluno, resultado, aluno):
        if not aluno or not str(aluno).strip():
            raise ValueError("O nome do aluno é obrigatório para salvar a correção.")

        correcao = {
            "questao_id": questao_id,
            "aluno": aluno.strip(),
            "resposta_aluno": resposta_aluno,
            "nota": resultado["nota"],
            "feedback": resultado["justificativa"],
            "origem": "automatica"
        }

        # Salva no histórico
        self.correction_repository.add(correcao)

        # Adiciona ao banco vetorial
        self.retriever.add(
            questao_id=questao_id,
            resposta=resposta_aluno,
            nota=resultado["nota"],
            feedback=resultado["justificativa"],
            aluno=aluno.strip()
        )

        
        