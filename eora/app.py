from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from socketio import ASGIApp

from eora.redis.redis import redis_async
from eora.services.portfolio import PortfolioService
from eora.routers.ws import sio


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_async.initialize()
    await redis_async.redis.flushall()

    await PortfolioService(redis_async=redis_async).load_data()
    print('end parser')

    yield

    await redis_async.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/socket.io", socketio.ASGIApp(sio))


from eora.routers.answers import router as answer_router
from eora.routers.web import router as web_router


app.include_router(answer_router)
app.include_router(web_router)
