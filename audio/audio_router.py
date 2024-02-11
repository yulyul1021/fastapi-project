from fastapi import APIRouter, UploadFile, File
from typing import Annotated
from fastapi import Depends, Request

from starlette.templating import Jinja2Templates

from sqlalchemy.orm import Session

import models
from database import get_db

import speech_recognition as sr


router = APIRouter(prefix="/audio")
templates = Jinja2Templates(directory="templates")

AUDIO_DIR = "file/"


@router.get("/")
def audio(request: Request):
    return templates.TemplateResponse("audio.html", {"request": request})


@router.post("/")
async def post_audio(request: Request, db: Annotated[Session, Depends(get_db)], file: Annotated[UploadFile, File()]):
    filepath = f"{AUDIO_DIR}{file.filename}"

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    r = sr.Recognizer()
    wavfile = sr.AudioFile(filepath)
    with wavfile as source:
        data = r.record(source)
    text = r.recognize_google(data, language="ko-KR")

    new_audio = models.Audio(filepath=file.filename, text=text)
    db.add(new_audio)
    db.commit()
    print(new_audio.filepath, new_audio.text)
    return templates.TemplateResponse("audio.html", {"request": request, "audio": new_audio})