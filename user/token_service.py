from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status

import os


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
