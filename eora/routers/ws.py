import socketio
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from eora.services.answers import AnswerService
from eora.services.llm import LLMService
from eora.dto.questions import QuestionDTO


router = APIRouter()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.on("connect")
async def connect(sid, environ):
    print(f"Клиент подключился: {sid}")


@sio.on("ask")
async def handle_ask(sid, data):
    question_text = data.get("text", "").strip()
    if not question_text:
        return

    llm_service = LLMService()
    answer_service = AnswerService(llm_service=llm_service)
    answer_dto = await answer_service.get_answer(
        QuestionDTO(text=question_text)
    )
    await sio.emit("response", {"text": answer_dto.text}, room=sid)


@sio.on("disconnect")
async def disconnect(sid):
    print(f"Клиент отключился: {sid}")
