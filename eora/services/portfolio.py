import asyncio
from typing import Optional

import httpx
from bs4 import BeautifulSoup


class PortfolioService:
    def __init__(
        self,
        redis_async,
        urls: list[str] = None,
        portfolio_key: str = None
    ):
        self.redis_async = redis_async
        self.portfolio_key = (
            "eora:portfolio" if not portfolio_key else portfolio_key
        )
        self.urls = [
            "https://eora.ru/cases/promyshlennaya-bezopasnost",
            "https://eora.ru/cases/lamoda-systema-segmentacii-i-poiska-po-pohozhey-odezhde",
            "https://eora.ru/cases/navyki-dlya-golosovyh-assistentov/karas-golosovoy-assistent",
            "https://eora.ru/cases/assistenty-dlya-gorodov",
            "https://eora.ru/cases/avtomatizaciya-v-promyshlennosti/chemrar-raspoznovanie-molekul",
            "https://eora.ru/cases/zeptolab-skazki-pro-amnyama-dlya-sberbox",
            "https://eora.ru/cases/goosegaming-algoritm-dlya-ocenki-igrokov",
            "https://eora.ru/cases/dodo-pizza-robot-analitik-otzyvov",
            "https://eora.ru/cases/ifarm-nejroset-dlya-ferm",
            "https://eora.ru/cases/zhivibezstraha-navyk-dlya-proverki-rodinok",
            "https://eora.ru/cases/sportrecs-nejroset-operator-sportivnyh-translyacij",
            "https://eora.ru/cases/avon-chat-bot-dlya-zhenshchin",
            "https://eora.ru/cases/navyki-dlya-golosovyh-assistentov/navyk-dlya-proverki-loterejnyh-biletov",
            "https://eora.ru/cases/computer-vision/iss-analiz-foto-avtomobilej",
            "https://eora.ru/cases/purina-master-bot",
            "https://eora.ru/cases/skinclub-algoritm-dlya-ocenki-veroyatnostej",
            "https://eora.ru/cases/skolkovo-chat-bot-dlya-startapov-i-investorov",
            "https://eora.ru/cases/purina-podbor-korma-dlya-sobaki",
            "https://eora.ru/cases/purina-navyk-viktorina",
            "https://eora.ru/cases/dodo-pizza-pilot-po-avtomatizacii-kontakt-centra",
            "https://eora.ru/cases/dodo-pizza-avtomatizaciya-kontakt-centra",
            "https://eora.ru/cases/icl-bot-sufler-dlya-kontakt-centra",
            "https://eora.ru/cases/s7-navyk-dlya-podbora-aviabiletov",
            "https://eora.ru/cases/workeat-whatsapp-bot",
            "https://eora.ru/cases/absolyut-strahovanie-navyk-dlya-raschyota-strahovki",
            "https://eora.ru/cases/kazanexpress-poisk-tovarov-po-foto",
            "https://eora.ru/cases/kazanexpress-sistema-rekomendacij-na-sajte",
            "https://eora.ru/cases/intels-proverka-logotipa-na-plagiat",
            "https://eora.ru/cases/karcher-viktorina-s-voprosami-pro-uborku",
            "https://eora.ru/cases/chat-boty/purina-friskies-chat-bot-na-sajte",
            "https://eora.ru/cases/nejroset-segmentaciya-video",
            "https://eora.ru/cases/chat-boty/essa-nejroset-dlya-generacii-rolikov",
            "https://eora.ru/cases/qiwi-poisk-anomalij",
            "https://eora.ru/cases/frisbi-nejroset-dlya-raspoznavaniya-pokazanij-schetchikov",
            "https://eora.ru/cases/skazki-dlya-gugl-assistenta",
            "https://eora.ru/cases/chat-boty/hr-bot-dlya-magnit-kotoriy-priglashaet-na-sobesedovanie",
        ] if not urls else urls
        self.data = {}

    async def fetch_page(
        self,
        client: httpx.AsyncClient,
        url: str
    ) -> Optional[dict]:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            html = response.text

            soup = BeautifulSoup(html, "html.parser")

            for tag in soup(
                ["script", "style", "nav", "footer", "header"]
            ):
                tag.decompose()

            title_tag = soup.find("title") or soup.find("h1")
            title = title_tag.get_text(
                strip=True
            ) if title_tag else url.split("/")[-1]

            text = soup.get_text(separator=" ", strip=True)

            return {"title": title, "content": text, "url": url}
        except Exception:
            return

    async def parse(self, urls: list) -> dict[str, dict]:
        """Парсит все URL, если данные ещё не загружены."""
        if self.data:
            return self.data

        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_page(client, url) for url in urls]
            results = await asyncio.gather(*tasks)

        self.data = {item["url"]: item for item in results if item}
        return self.data

    async def load_data(self) -> None:
        cached_data = await self.redis_async.get_json(self.portfolio_key)
        if cached_data:
            return cached_data

        clean_urls = [url.strip() for url in self.urls]
        data = await self.parse(urls=clean_urls)

        if not data:
            print("Error parsing")
            return
        await self.redis_async.set_json(self.portfolio_key, data)
        self.data = data
        return data

    async def get_data(self) -> dict:
        if not self.data:
            await self.load_data()
        return self.data
