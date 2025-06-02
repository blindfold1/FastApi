import logging
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "Fitness Trainers API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "fitness_trainers"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"  # В продакшене использовать безопасный ключ
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # File upload
    UPLOAD_DIR: Path = Path("static/uploads")
    MAX_FILE_SIZE: int = 5_242_880  # 5MB

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
