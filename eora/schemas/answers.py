from pydantic import BaseModel


class AnswerSchema(BaseModel):
    text: str
