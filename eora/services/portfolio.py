import asyncio
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from eora.config.base import Config


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
        self.urls = urls if urls else Config.PORTFOLIO_URLS
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
        # if self.data:
        #     return self.data

        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_page(client, url) for url in urls]
            results = await asyncio.gather(*tasks)

        self.data = {item["url"]: item for item in results if item}
        return self.data

    async def load_data(self) -> Optional[dict]:
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
        return self.data if self.data else {}

    def get_portfolio_urls(self, filepath: str) -> Optional[list[str]]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                urls = [
                    line.strip() for line in f
                    if line.strip() and not line.startswith("#")
                ]
            return urls
        except Exception as e:
            print(e)
