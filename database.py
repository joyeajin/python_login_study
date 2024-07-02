from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


DB_URL = "mysql+pymysql://root:yeajin1009@localhost/goya_app_db"
DB_URL_2 = (
    "mysql+pymysql://root:cindy2018!@52.79.226.104:3306/devfocappdbtest?charset=utf8mb4"
)

engine = create_engine(DB_URL, pool_recycle=500)  # DB 커넥션 풀 생성
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)  # DB접속을 위한 클래스

# engine_2 = create_engine(DB_URL_2, pool_recycle=500)
# SessionLocal_2 = sessionmaker(autocommit=False, autoflush=False, bind=engine_2)
# ScopedSessionLocal_2 = scoped_session(SessionLocal_2)

Base = declarative_base()  # Base 클래스는 DB 모델 구성할 때 사용


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 요청마다 새로운 데이터베이스 연결을 생성하고 요청이 완료되면 연결을 닫도록,,,
def get_db_2():
    engine_2 = create_engine(
        DB_URL_2,
        pool_recycle=500,
        connect_args={
            "connect_timeout": 10,
            "init_command": "SET time_zone = '+00:00'",
        },
    )
    SessionLocal_2 = sessionmaker(autocommit=False, autoflush=False, bind=engine_2)
    db = SessionLocal_2()
    try:
        yield db
    finally:
        db.close()
