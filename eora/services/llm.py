import openai

from eora.services.portfolio import PortfolioService
from eora.config.base import Config
from eora.redis.redis import redis_async


PROMPT_TEMPLATE = """
Вы — официальный ассистент компании EORA. 
Ваша задача — отвечать на вопросы клиентов, 
используя ТОЛЬКО информацию из портфолио ниже.

ВАЖНО:
- Не выдумывайте проекты.
- Если не знаете ответа — скажите: "Я не нашёл подходящего кейса в портфолио."
- Указывайте номера ссылок в формате [1], [2] сразу после упоминания проекта.
- В конце перечислите все использованные источники.

ПОРТФОЛИО:
{portfolio_context}

ВОПРОС: {question}

ОТВЕТ:
"""


class LLMService:
    def __init__(
        self,
        portfolio_service = None,
        prompt_template = None
    ):
        self.portfolio_service = (
            PortfolioService(redis_async=redis_async)
            if not portfolio_service else portfolio_service
        )
        self.prompt_template=(
            PROMPT_TEMPLATE if not prompt_template else prompt_template
        )

    def _build_portfolio_context(self, cases: list[dict]) -> str:
        context = ""
        for i, case in enumerate(cases, 1):
            title = case.get("title", "Без названия")
            url = case.get("url", "").strip()
            content = case.get("content", "")[:500]
            context += f"[{i}] {title}\n{content}...\nURL: {url}\n\n"
        return context

    async def ask(self, question: str) -> str:
        portfolio = await self.portfolio_service.get_data()
        relevant_cases = self._find_relevant_cases(
            list(portfolio.values()), question
        )

        if not relevant_cases:
            return "Я не нашёл подходящего кейса в портфолио."

        context = self._build_portfolio_context(relevant_cases)
        prompt = self.prompt_template.format(
            portfolio_context=context,
            question=question
        )

        try:
            client = openai.OpenAI(
                api_key=Config.OPENROUTER_API_KEY,
                base_url=Config.OPENROUTER_API_BASE
            )

            response = client.chat.completions.create(
                model=Config.LLM_MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error Request LLM: {str(e)}"

    def _find_relevant_cases(self, all_cases: list[dict], query: str) -> list[dict]:
        keywords = query.lower().split()
        relevant = []
        for case in all_cases:
            text = f"{case.get('title', '')} {case.get('content', '')}".lower()
            if any(kw in text for kw in keywords):
                relevant.append(case)
        return relevant[:5]
