from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL bağlantı bilgileri
# Şifreyi aynen ALTER USER komutunda kullandığın gibi yaz
DATABASE_URL = (
    "postgresql+psycopg://esp32cam_api:ZjZM3N9xB2wF3ZCJ8YC3RwN3gKjf326a"
    "@localhost/esp32cam_db"
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
