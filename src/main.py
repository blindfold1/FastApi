from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse  # Добавьте этот импорт
from fastapi.staticfiles import StaticFiles

from src.api.routes.clients import  clients_router
from src.db.database import  database_router
from src.api.routes.auth import auth_router

app = FastAPI()

# Подключите роутеры
app.include_router(clients_router)
app.include_router(database_router)
app.include_router(auth_router)

static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Обработка favicon.ico
@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("static/favicon.ico")
@app.get("/")
async def root():
    return {"message": "Hello World"}