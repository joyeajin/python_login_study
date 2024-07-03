from sqlalchemy import Column, Integer, VARCHAR, DateTime, TEXT, Date
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "Users"

    user_no = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(VARCHAR(10), nullable=False)
    email = Column(VARCHAR(100), nullable=False, unique=True)
    hashed_pw = Column(VARCHAR(100), nullable=False)
    role = Column(VARCHAR(20), nullable=False, default="MEMBER")
    status = Column(VARCHAR(1), nullable=False, default="1")
    regdate = Column(DateTime, nullable=False, default=datetime.now)


class Member(Base):
    __tablename__ = "member_test"

    idx = Column(Integer, primary_key=True, index=True)
    userId = Column(TEXT, unique=True, index=True)
    nickname = Column(TEXT)
    type = Column(Integer)
    isPayment = Column(Integer)
    endDate = Column(TEXT)


class AppMember(Base):
    __tablename__ = "tbl_member"

    idx = Column(Integer, primary_key=True, index=True)
    user_id = Column(VARCHAR(50), unique=True, index=True)
    nickname = Column(VARCHAR(20))
    type = Column(Integer)
    is_payment = Column(Integer)
    end_date = Column(Date)
    is_delete = Column(Integer)  # 탈퇴 여부
