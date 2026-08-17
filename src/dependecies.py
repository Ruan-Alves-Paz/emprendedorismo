from repositories.QuestionRepository import QuestionRepository
from repositories.CorrectionRepository import CorrectionRepository
from repositories.ExamRepository import ExamRepository

from services.QuestionService import QuestionService
from services.CorrectionService import CorrectionService
from services.ExamCorrectionService import ExamCorrectionService

from retriever import Retriever
from evaluator import Evaluator
from ocr import OCRExtractor

question_repository = QuestionRepository()
correction_repository = CorrectionRepository()
exam_repository = ExamRepository()

retriever = Retriever()
evaluator = Evaluator()
ocr_extractor = OCRExtractor()

question_service = QuestionService(question_repository)

correction_service = CorrectionService(
    question_repository,
    correction_repository,
    retriever,
    evaluator
)

exam_correction_service = ExamCorrectionService(correction_service)