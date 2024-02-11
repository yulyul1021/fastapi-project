import uuid
from datetime import timedelta, datetime

from fastapi import APIRouter, Form
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

import models
from database import get_db

from passlib.context import CryptContext

router = APIRouter(prefix="/user")
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = "afd0afbc24f7f84872ae987bb95aeaaa308b68067d38e0206f33bb26aa25f3b8"
ALGORITHM = "HS256"

##################################
import smtplib, ssl

SMTP_SSL_PORT = 465  # SSL connection
SMTP_SERVER = "smtp.gmail.com"

SENDER_EMAIL = "yulyul102102@gmail.com"
SENDER_PASSWORD = "vsnc vbkd dxlp njfr"

context = ssl.create_default_context()


def send_email(receiver_email, auth_key):
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_SSL_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email,
                        f"You can complete your registration by clicking the following link.\n"
                        f"http://127.0.0.1:8000/user/email_auth/{auth_key}", )


#####################################


@router.get("/")
def user_home(request: Request):
    return templates.TemplateResponse("user_home.html", {"request": request})


@router.get("/signup")
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup")
def signup(user_email: Annotated[str, Form()], password1: Annotated[str, Form()],
           db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(models.User.user_email == user_email).first()

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 회원입니다.")

    new_user = models.User(user_email=user_email,
                           password=pwd_context.hash(password1),
                           auth_key=str(uuid.uuid4()))
    db.add(new_user)
    db.commit()
    send_email(new_user.user_email, new_user.auth_key)
    return RedirectResponse(url=router.url_path_for("user_home"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/email_auth/{auth_key}")
def email_auth(auth_key: str, db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(models.User.auth_key == auth_key).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="존재하지 않는 회원입니다.")

    user.is_active = True
    db.commit()
    return "회원가입이 완료되었습니다."


@router.get("/signin")
def signin_form(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})


@router.post("/signin")
def signin(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
           db: Annotated[Session, Depends(get_db)]):

    user = db.query(models.User).filter(models.User.user_email == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ID 혹은 비밀번호가 올바르지 않습니다.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비활성된 회원입니다. 이메일 인증을 완료해주세요.")

    # access token 만들기
    data = {
        "sub": user.user_email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    # 쿠키에 토큰 저장
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])


@router.get("/signout")
def signout(response: Response):
    response.delete_cookie(key="access_token")
    return "로그아웃 성공"