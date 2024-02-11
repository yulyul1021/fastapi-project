from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, Request, Form, status

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from sqlalchemy.orm import Session

import models
from database import get_db
from todo import todo_schema

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    todos = db.query(models.Todo).all()
    return templates.TemplateResponse("index.html",
                                      {"request": request, "todo_list": todos})


@router.post("/add")
def add(title: Annotated[str, Form()], db: Annotated[Session, Depends(get_db)]):
    new_todo = models.Todo(title=title)
    db.add(new_todo)
    db.commit()
    return RedirectResponse(url=router.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/update/{todo_id}")
def update(todo_id: int, db: Annotated[Session, Depends(get_db)]):
    todo = db.query(models.Todo).get(todo_id)
    todo.complete = not todo.complete
    db.commit()
    return RedirectResponse(url=router.url_path_for("home"))


@router.get("/delete/{todo_id}")
def delete(todo_id: int, db: Annotated[Session, Depends(get_db)]):
    todo = db.query(models.Todo).get(todo_id)
    db.delete(todo)
    db.commit()
    return RedirectResponse(url=router.url_path_for("home"))


@router.get("/schema", response_model=list[todo_schema.Todo])
def schema(db: Annotated[Session, Depends(get_db)]):
    todo = db.query(models.Todo).all()
    return todo