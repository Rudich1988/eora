from contextlib import asynccontextmanager

from fastapi import FastAPI

from eora.redis.redis import redis_async
from eora.services.portfolio import PortfolioService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_async.initialize()
    data = await PortfolioService(redis_async=redis_async).load_data()
    print('Redis инициализирован')
    print(data)

    yield

    await redis_async.close()


app = FastAPI(lifespan=lifespan)


from eora.routers.answers import router as answer_router


app.include_router(answer_router)
