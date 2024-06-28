from pydantic import BaseModel, EmailStr, field_validator
from fastapi import HTTPException


class Token(BaseModel):
    access_token: str
    token_type: str


class NewUserForm(BaseModel):
    email: EmailStr
    name: str
    phone: str
    password: str

    @field_validator("email", "name", "phone", "password")
    def check_empty(cls, v):
        if not v or v.isspace():
            raise HTTPException(status_code=422, detail="필수항목을 입력해주세요.")
        return v

    @field_validator("phone")
    def check_phone(cls, v):
        phone = v
        if "-" not in v or len(phone) != 13:
            raise HTTPException(
                status_code=422, detail="올바른 형식의 번호를 입력해주세요."
            )
        return phone

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise HTTPException(
                status_code=422,
                detail="비밀번호는 8자리 이상 영문과 숫자를 포함하여 작성해주세요.",
            )

        if not any(char.isdigit() for char in v):
            raise HTTPException(
                status_code=422,
                detail="비밀번호는 8자리 이상 영문과 숫자를 포함하여 작성해주세요.",
            )

        if not any(char.isalpha() for char in v):
            raise HTTPException(
                status_code=422,
                detail="비밀번호는 8자리 이상 영문과 숫자를 포함하여 작성해주세요.",
            )

        return v
