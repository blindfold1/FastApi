
import logging
from logging.handlers import RotatingFileHandler

DATABASE_URL="postgresql+asyncpg://postgres:3103@localhost:5432/users"
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 📝 Логирование
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOG_FILE = "app.log"

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("uvicorn.error")
