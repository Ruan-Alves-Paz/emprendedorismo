class QuestionService:

    def __init__(self, repository):
        self.repository = repository

    def list_questions(self):
        return self.repository.get_all()

    def get_question(self, question_id):
        return self.repository.get_by_id(question_id)

    def get_question_by_enunciado(self, enunciado):
        return self.repository.get_by_enunciado(enunciado)

    def create_question(
        self,
        enunciado,
        resposta_modelo,
        criterios,
        nota_maxima
    ):

        if not enunciado.strip():
            raise ValueError("O enunciado é obrigatório.")

        if not resposta_modelo.strip():
            raise ValueError("A resposta modelo é obrigatória.")

        questoes = self.repository.get_all()

        if len(questoes) == 0:
            novo_id = 1
        else:
            novo_id = max(q["questao_id"] for q in questoes) + 1

        questao = {
            "questao_id": novo_id,
            "enunciado": enunciado,
            "criterios": criterios,
            "resposta_modelo": resposta_modelo,
            "nota_maxima": nota_maxima
        }

        self.repository.add(questao)

        return questao