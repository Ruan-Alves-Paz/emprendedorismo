from repositories.QuestionRepository import QuestionRepository
from repositories.CorrectionRepository import CorrectionRepository
from repositories.ExamRepository import ExamRepository
from repositories.ExamModelRepository import ExamModelRepository

from services.QuestionService import QuestionService
from services.CorrectionService import CorrectionService
from services.ExamCorrectionService import ExamCorrectionService
from services.ExamModelService import ExamModelService

from retriever import Retriever
from evaluator import Evaluator
from ocr import OCRExtractor

question_repository = QuestionRepository()
correction_repository = CorrectionRepository()
exam_repository = ExamRepository()
exam_model_repository = ExamModelRepository()

retriever = Retriever()
evaluator = Evaluator()
ocr_extractor = OCRExtractor()

question_service = QuestionService(question_repository)
exam_model_service = ExamModelService(exam_model_repository, question_repository)

correction_service = CorrectionService(
    question_repository,
    correction_repository,
    retriever,
    evaluator
)

exam_correction_service = ExamCorrectionService(correction_service)