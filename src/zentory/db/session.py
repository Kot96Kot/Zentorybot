from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from zentory.core.config import get_settings

engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db_session() -> Session:
    with SessionLocal() as session:
        yield session
