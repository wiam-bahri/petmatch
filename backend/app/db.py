"""SQLite (local) ou PostgreSQL (production, via DATABASE_URL, pilote psycopg 3) avec SQLAlchemy."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE, 'petmatch.db')}").strip().strip("'\"")
# Normalise n'importe quel URL PostgreSQL vers le pilote psycopg (v3)
for prefix in ("postgres://", "postgresql://", "postgresql+psycopg2://"):
    if DB_URL.startswith(prefix):
        DB_URL = "postgresql+psycopg://" + DB_URL[len(prefix):]
        break
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,                       # reconnecte si la base s'est endormie
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
