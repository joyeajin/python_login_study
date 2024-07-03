from sqlalchemy.orm import Session
from models import User, Member, AppMember
from user.user_schema import NewUserForm

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_email(email: str, db: Session):
    # return db.query(User).filter(User.email == email).first()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception as e:
        print(f"에러,,,,: {e}")
        return None


def get_user_name(name: str, db: Session):
    # print("-----", db.query(User))
    # return db.query(User).filter(User.user_name == name).first()
    try:
        user = db.query(User).filter(User.user_name == name).first()
        return user
    except Exception as e:
        print(f"에러,,,,: {e}")
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
    # print("plain_password", plain_password)
    # print("hashed_password", hashed_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_member_by_user_id(user_id: str, db: Session):
    try:
        # print("db", db.query(Member))
        member = db.query(Member).filter(Member.userId == user_id).first()
        return member
    except Exception as e:
        print(f"멤버 에러,,,,: {e}")
        return None


def get_app_member_by_user_id(user_id: str, db: Session):
    print("user_id", user_id)
    print("db", db)

    try:
        app_member = db.query(AppMember).filter(AppMember.user_id == user_id).first()
        # print("####", db.query(AppMember).filter(AppMember.user_id == user_id))
        # print("app_member", app_member)
        print("app_member return", app_member)
        return app_member

    except Exception as e:
        print(f"앱 멤버 에러,,,,: {e}")
        return None


def get_app_member_is_delete(user_id: str, db: Session):
    try:
        app_member_is_delete = (
            db.query(AppMember)
            .filter(AppMember.user_id == user_id, AppMember.is_delete == 1)
            .first()
        )
        return app_member_is_delete

    except Exception as e:
        print(f"앱 멤버 탈퇴여부 에러,,,,: {e}")
        return None
