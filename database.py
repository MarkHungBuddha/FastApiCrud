# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# 建立資料庫連線 URL
# 格式: 'postgresql://<user>:<password>@<hostname>:<port>/<dbname>'
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:{settings.database_password}@"
    f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)

# 建立 SQLAlchemy 引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 建立一個 SessionLocal 類別，這個類別的每個實例都將是一個資料庫 session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立一個 Base 類別，之後我們的 ORM 模型會繼承這個類別
Base = declarative_base()

# Dependency: 建立並提供一個資料庫 session，並在請求結束後關閉它
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()