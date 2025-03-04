from datetime import timedelta
from sqlalchemy.orm import Session
from database import get_db, get_db_2
from fastapi import APIRouter, Depends, HTTPException, status, Response, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from user.user_schema import MemberSchema, NewUserForm, Token, AppMemberSchema
from user.user_crud import (
    UserAppMemberService,
    verify_password,
)
from user.token_service import TokenService
from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv

# env 파일에 있는 환경변수 가져옴
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

app = APIRouter(prefix="/user")

token_service = TokenService()


@app.get("/test")
async def user_test():
    return "test"


# 회원가입!
@app.post(path="/signup")
async def signup(new_user: NewUserForm, db: Session = Depends(get_db)):

    user_service = UserAppMemberService(db)

    # 회원 존재 여부 확인
    user = user_service.get_user_email(new_user.email)

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 가입한 회원입니다."
        )

    # 회원가입
    user_service.create_user(new_user)

    return HTTPException(status_code=status.HTTP_200_OK, detail="회원가입 성공")


# 로그인!
@app.post(path="/login")
async def login(
    response: Response,
    login_form: OAuth2PasswordRequestForm = Depends(),  # OAuth2PasswordRequestForm 사용해서 비밀번호나 아이디가 누락되면 fastApi가 자동으로 422 Unprocessable Entity 상태 코드 반환함
    db: Session = Depends(get_db),
    db_2: Session = Depends(get_db_2),
):

    user_service = UserAppMemberService(db)
    app_member_service = UserAppMemberService(db_2)

    # id누락
    if not login_form.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 20003, "message": "아이디를 입력해주세요."},
        )

    # 비번 누락
    if not login_form.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 20004, "message": "비밀번호를 입력해주세요."},
        )

    # 회원 존재 여부 확인
    user = user_service.get_user_email(login_form.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 10000, "message": "존재하지 않는 회원입니다."},
        )

    # 비밀번호 검증
    res = verify_password(login_form.password, user.hashed_pw)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 10003, "message": "잘못된 비밀번호 입니다."},
        )

    # 탈퇴한 회원인지 확인
    is_delete = app_member_service.get_app_member_is_delete(login_form.username)

    if is_delete:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 10004, "message": "탈퇴한 회원입니다."},
        )

    # member = get_member_by_user_id(login_form.username, db)
    # if not member:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="회원 정보를 찾을 수 없습니다.",
    #     )

    app_member = app_member_service.get_app_member_by_user_id(login_form.username)
    # tbl_member 테이블에 정보가 없을 때
    if not app_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="회원 정보를 찾을 수 없습니다.",
        )

    # app_member_data = {
    #     "idx": app_member.idx,
    #     "user_id": app_member.user_id,
    #     "nickname": app_member.nickname,
    #     "type": app_member.type,
    #     "is_payment": app_member.is_payment,
    #     "end_date": app_member.end_date,
    # }
    # app_member_pydantic = AppMemberSchema(
    #     **app_member_data
    # )  # **member_data : member_data딕셔너리 언패킹

    # 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token, expired_in = token_service.create_token(
        data={"sub": user.user_name},
        expires_delta=access_token_expires,
        token_type="access",
    )
    refresh_token = token_service.create_token(
        data={"sub": user.user_name},
        expires_delta=refresh_token_expires,
        token_type="refresh",
    )

    # member_data = {
    #     "idx": member.idx,
    #     "userId": member.userId,
    #     "nickname": member.nickname,
    #     "type": member.type,
    #     "isPayment": member.isPayment,
    #     "endDate": member.endDate,
    # }
    # member_pydantic = MemberSchema(
    #     **member_data
    # )  # **member_data : member_data딕셔너리 언패킹

    # member_pydantic = MemberSchema.from_orm(member)

    # FastAPI와 Pydantic을 사용하여 데이터베이스 객체를 Pydantic 모델로 변환
    app_member_pydantic = AppMemberSchema.from_orm(app_member)

    # access_token 쿠키에 저장
    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=access_token_expires,
        httponly=True,
    )

    code = 0
    result = {
        "code": code,
        "data": Token(
            grant_type="Bearer",
            access_token=access_token,
            refresh_token=refresh_token,
            expired_in=expired_in,
            member=app_member_pydantic,
        ),
    }

    return result


# 액세스 토큰 갱신 엔드포인트
@app.post("/refresh")
async def refresh_token(auth_token: str = Header(...), db: Session = Depends(get_db)):

    try:
        token_type, token = auth_token.split()

        if token_type != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰 타입입니다.",
            )

        access_token = token_service.refresh_access_token(token, db)
        return {"access_token": access_token, "grant_type": "Bearer"}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 올바르지 않습니다."
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"토큰 처리 중 에러 발생: {e}",
        )


# 로그아웃!
@app.get(path="/logout")
async def logout(response: Response, request: Request):
    # access_token = request.cookies.get("access_token")

    # 쿠키 삭제
    response.delete_cookie(key="access_token")

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"detail": "로그아웃 완료"}
    )


# @app.post("/refresh")
# async def refresh_token(
#     refresh_token: str = Header(...), db: Session = Depends(get_db)
# ):
#     # print("##########", token)

#     try:
#         # print("Received token:", token)
#         token = refresh_token.split(" ")[1]
#         # print("SECRET_KEY:", SECRET_KEY)
#         # print("ALGORITHM:", ALGORITHM)

#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         print("Decoded payload:", payload)

#         username: str = payload.get("sub")
#         print("username:", username)

#         if username is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token username",
#             )
#         user = get_user_name(username, db)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token user"
#             )
#     except JWTError as e:
#         print("JWTError:", e)
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWTError")

#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

#     access_token = create_access_token(
#         data={"sub": username}, expires_delta=access_token_expires
#     )
#     refresh_token = create_refresh_token(
#         data={"sub": username}, expires_delta=refresh_token_expires
#     )


#     return Token(
#         access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
#     )
