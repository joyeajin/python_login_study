from sqlalchemy.orm import Session
from models import User, Member, AppMember
from user.user_schema import NewUserForm
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status

from passlib.context import CryptContext

import os
from dotenv import load_dotenv

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserAppMemberService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_email(self, email: str):
        try:
            user = self.db.query(User).filter(User.email == email).first()
            return user
        except Exception as e:
            print(f"get_user_email 에러: {e}")
            return None

    def get_user_name(self, name: str):
        try:
            user = self.db.query(User).filter(User.user_name == name).first()
            return user
        except Exception as e:
            print(f"get_user_name 에러: {e}")
            return None

    # def get_member_by_user_id(self, user_id: str):
    #     try:
    #         member = self.db.query(Member).filter(Member.userId == user_id).first()
    #         return member
    #     except Exception as e:
    #         print(f"get_member_by_user_id 에러: {e}")
    #         return None

    def get_app_member_by_user_id(self, user_id: str):
        try:
            app_member = (
                self.db.query(AppMember).filter(AppMember.user_id == user_id).first()
            )
            return app_member
        except Exception as e:
            print(f"get_app_member_by_user_id 에러: {e}")
            return None

    def get_app_member_is_delete(self, user_id: str):
        try:
            app_member_is_delete = (
                self.db.query(AppMember)
                .filter(AppMember.user_id == user_id, AppMember.is_delete == 1)
                .first()
            )
            return app_member_is_delete
        except Exception as e:
            print(f"get_app_member_is_delete 에러: {e}")
            return None

    def create_user(new_user: NewUserForm, db: Session):
        hashed_pw = pwd_context.hash(new_user.password)
        user = User(
            user_name=new_user.name,
            email=new_user.email,
            hashed_pw=hashed_pw,
        )
        db.add(user)
        db.commit()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


#### 토큰 관련 함수들!
class TokenService:
    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")

    # 토큰 생성 함수
    def create_token(self, data: dict, expires_delta: timedelta, token_type: str):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        if token_type == "access":
            return encoded_jwt, expire
        else:
            return encoded_jwt

    def refresh_access_token(self, token: str, db):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="리프레시 토큰에 username(sub)이 없습니다.",
                )

            # User에서 조회
            user_service = UserAppMemberService(db)

            user = user_service.get_user_name(username)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": 10000, "message": "존재하지 않는 회원입니다."},
                )

            # 새로운 액세스 토큰 생성
            access_token_expires = timedelta(
                minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
            )
            access_token = self.create_token(
                data={"sub": username},
                expires_delta=access_token_expires,
                token_type="access",
            )

            return access_token[0]

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"리프레시 토큰 디코딩 에러: {e}",
            )

    # 토큰 유효성 검사
    # def verify_access_token(self, token: str):
    #     try:
    #         payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
    #         return payload
    #     except JWTError as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail=f"액세스 토큰 디코딩 에러: {e}",
    #         )
