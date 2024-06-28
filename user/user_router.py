from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from database import get_db

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from user.user_schema import NewUserForm, Token
from user.user_crud import get_user, create_user, verify_password
from jose import jwt

import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = APIRouter(prefix="/user")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.get("/test")
async def user_test():
    return "test"


# 회원가입!
@app.post(path="/signup")
async def signup(new_user: NewUserForm, db: Session = Depends(get_db)):
    # 회원 존재 여부 확인
    user = get_user(new_user.email, db)

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 가입한 회원입니다."
        )

    # 회원가입
    create_user(new_user, db)

    return HTTPException(status_code=status.HTTP_200_OK, detail="회원가입 성공")


# 로그인!
@app.post(path="/login")
async def login(
    response: Response,
    login_form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # 회원 존재 여부 확인
    user = get_user(login_form.username, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 ID 입니다.",
        )

    # 로그인
    res = verify_password(login_form.password, user.hashed_pw)

    # 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires
    )

    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호를 잘못 입력하셨습니다.",
        )

    # return HTTPException(status_code=status.HTTP_200_OK, detail="로그인 성공")
    return Token(access_token=access_token, token_type="Bearer")
