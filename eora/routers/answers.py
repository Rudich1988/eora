from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from eora.schemas.answers import AnswerSchema
from eora.schemas.questions import QuestionSchema
from eora.dto.questions import QuestionDTO
from eora.services.answers import AnswerService
from eora.services.llm import LLMService

router = APIRouter(
    prefix='/answers',
    tags=['Orders']
)


@router.post('/', response_model=AnswerSchema)
async def get_answer(question: QuestionSchema):
    try:
        question = QuestionDTO(text=question.text)
        answer = await AnswerService(
            llm_service=LLMService()
        ).get_answer(question=question)
        answer_schema = AnswerSchema(text=answer.text)
        return answer_schema
    except Exception as e:
        return JSONResponse(
            content={'error': str(e)},
            status_code=500
        )
