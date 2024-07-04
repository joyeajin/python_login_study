from sqlalchemy.orm import Session
from models import User, Member, AppMember
from user.user_schema import NewUserForm

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#### 회원 관련 함수들!
class UserAppMemberService:
    def __init__(self, db: Session):
        self.db = db

    # User DB에서 입력한 email이 있나 체크하는 함수
    def get_user_email(self, email: str):
        try:
            user = self.db.query(User).filter(User.email == email).first()
            return user
        except Exception as e:
            print(f"get_user_email 에러: {e}")
            return None

    # User DB에서 입력한 name이 있나 확인하는 함수
    # def get_user_name(self, name: str):
    #     try:
    #         user = self.db.query(User).filter(User.user_name == name).first()
    #         return user
    #     except Exception as e:
    #         print(f"get_user_name 에러: {e}")
    #         return None

    # def get_member_by_user_id(self, user_id: str):
    #     try:
    #         member = self.db.query(Member).filter(Member.userId == user_id).first()
    #         return member
    #     except Exception as e:
    #         print(f"get_member_by_user_id 에러: {e}")
    #         return None

    # AppMember DB에서 입력한 user_id와 일치하는 user_id가 있는지 체크하는 함수
    def get_app_member_by_user_id(self, user_id: str):
        try:
            app_member = (
                self.db.query(AppMember).filter(AppMember.user_id == user_id).first()
            )
            return app_member
        except Exception as e:
            print(f"get_app_member_by_user_id 에러: {e}")
            return None

    # AppMember DB에서 입력한 user_id와 일치하는 user_id가 있고 그 회원이 탈퇴한 회원인지 체크하는 함수
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

    # 입력한 정보들과 hash된 패스워드를 User DB에 넣는 함수
    def create_user(new_user: NewUserForm, db: Session):
        hashed_pw = pwd_context.hash(new_user.password)
        user = User(
            user_name=new_user.name,
            email=new_user.email,
            hashed_pw=hashed_pw,
        )
        db.add(user)
        db.commit()


# 입력한 비밀번호와 hash된 비밀번호가 일치하는지 확인하는 함수
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
