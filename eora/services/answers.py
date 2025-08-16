from eora.dto.questions import QuestionDTO
from eora.dto.answers import AnswerDTO
from eora.redis.redis import redis_async


class AnswerService:
    def __init__(self, llm_service):
        self.llm = llm_service
        self.redis = redis_async

    def _get_cache_key(self, text: str) -> str:
        return "answer:" + text.strip().lower().replace("?", "").replace(" ", "_")

    async def check_answer(self, question: QuestionDTO):
        return await self.redis.get_str(key=question)

    async def get_answer(
        self,
        question: QuestionDTO
    ) -> AnswerDTO:
        question_key = self._get_cache_key(question.text)
        answer = await self.check_answer(question_key)
        if answer:
            return AnswerDTO(text=answer)

        answer_text = await self.llm.ask(question.text)

        await self.redis.set(question_key, answer_text)

        return AnswerDTO(text=answer_text)

    async def delete_answer(
        self,
        question: QuestionDTO
    ):
        question_key = self._get_cache_key(question.text)
        await self.redis.delete(name=question_key)