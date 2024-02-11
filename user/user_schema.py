from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from fastapi import HTTPException


class UserCreate(BaseModel):
    user_email: EmailStr
    password1: str
    password2: str

    @field_validator("user_email", "password1", "password2")
    def check_empty(cls, v):
        if not v or v.isspace():
            raise HTTPException(status_code=422, detail="빈 값은 허용되지 않습니다.")
        return v

    @field_validator("password2")
    def password_match(cls, v, info: FieldValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            raise HTTPException(status_code=422, detail='비밀번호가 일치하지 않습니다.')
        return v
