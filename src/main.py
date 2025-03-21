from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

from src.api.routes import router  # Импорт основного роутера
from src.db.database import database_router

app = FastAPI(
    title = "MyApi",
    description= "Gymbro",
    docs_url = "/docs",
    openapi_url = "/openapi.json",
    swagger_ui_parameters={
        "favicon":"/static/favicon.ico",
    }
)




app.include_router(router)
app.include_router(database_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()



