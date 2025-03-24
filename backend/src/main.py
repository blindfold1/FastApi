from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.src.api.routes import router
from backend.src.db.database import database_router

app = FastAPI(
    title = "MyApi",
    description= "GymHelper",
    docs_url = "/docs",
    openapi_url = "/openapi.json",
    swagger_ui_parameters={
        "favicon":"/static/favicon.ico",
    }
)




app.include_router(router)
app.include_router(database_router)

app.mount("/static", StaticFiles(directory="static"), name="static")




origin = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



