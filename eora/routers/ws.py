import socketio
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from eora.services.answers import AnswerService
from eora.services.llm import LLMService
from eora.dto.questions import QuestionDTO
from eora.dto.answers import AnswerDTO
from eora.redis.redis import redis_async


router = APIRouter()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.on("connect")
async def connect(sid, environ):
    print(f"Клиент подключился: {sid}")


@sio.on("ask")
async def handle_ask(sid, data):
    try:
        question_text = data.get("text", "").strip()
        if not question_text:
            return

        llm_service = LLMService()
        answer_service = AnswerService(llm_service=llm_service)
        answer_dto = await answer_service.get_answer(
            QuestionDTO(text=question_text)
        )

        if "Error" in answer_dto.text:
            await answer_service.delete_answer(QuestionDTO(text=question_text))

            answer_dto = AnswerDTO(
                text="Произошла ошибка. Попробуйте обратиться еще раз"
            )
        await sio.emit("response", {"text": answer_dto.text}, room=sid)
    except Exception:
        await AnswerService(
            llm_service=LLMService()
        ).delete_answer(question=QuestionDTO(text=data.get("text", "").strip()))

        error_text = "Произошла ошибка. Попробуйте обратиться еще раз"
        await sio.emit("response", {"text": error_text}, room=sid)


@sio.on("disconnect")
async def disconnect(sid):
    print(f"Клиент отключился: {sid}")
