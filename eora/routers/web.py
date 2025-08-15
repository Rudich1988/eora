from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="eora/templates")


@router.get("/")
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
