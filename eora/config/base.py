import os

from dotenv import load_dotenv


load_dotenv()


class Config(object):
    REDIS_PORT = os.getenv('REDIS_PORT', "6379")
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME', 'mistralai/mistral-7b-instruct')
    OPENROUTER_API_BASE = os.getenv(
        'OPENROUTER_API_BASE',
        'https://openrouter.ai/api/v1'
    )