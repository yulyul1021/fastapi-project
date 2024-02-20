from fastapi import FastAPI
from starlette.staticfiles import StaticFiles


from todo import todo_router
from audio import audio_router
from user import user_router

import models
from database import engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.mount("/file", StaticFiles(directory="file"), name="file")
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(todo_router.router)
app.include_router(audio_router.router)
app.include_router(user_router.router)
