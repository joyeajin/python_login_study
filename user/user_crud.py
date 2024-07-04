from sqlalchemy.orm import Session
from models import User, Member, AppMember
from user.user_schema import NewUserForm

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#### 회원 관련 함수들!
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
