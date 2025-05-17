import logging
from logging.handlers import RotatingFileHandler

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:3103@localhost:5432/users"
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    USDA_API_KEY: str = "0yyvFkoxgTXuNul5HigxI6f6Z2FO7YDAzfbDirhv"
    MONGO_URI="mongodb+srv://sharafanovichkirill:3103@cluster0.4kamcli.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

file_handler = RotatingFileHandler(
    "app.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
