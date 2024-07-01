from sqlalchemy.orm import Session
from models import User
from user.user_schema import NewUserForm

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


def get_user_name(name: str, db: Session):
    # print("-----", db.query(User))
    # return db.query(User).filter(User.user_name == name).first()
    try:
        print("name", name)
        print("###", db.query(User).filter(User.user_name == name).first())

        user = db.query(User).filter(User.user_name == name).first()

        return user
    except Exception as e:
        print(f"에러,,,,: {e}")
        return None


def create_user(new_user: NewUserForm, db: Session):
    user = User(
        user_name=new_user.name,
        email=new_user.email,
        hashed_pw=pwd_context.hash(new_user.password),
    )
    db.add(user)
    db.commit()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password):
#     return pwd_context.hash(password)
