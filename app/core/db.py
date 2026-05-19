import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        url = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
        )
        _engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    return _engine

def fetch_all(query: str, params: dict = None) -> list[dict]:
    with get_engine().connect() as conn:
        result = conn.execute(text(query), params or {})
        keys = result.keys()
        return [dict(zip(keys, row)) for row in result.fetchall()]

def fetch_one(query: str, params: dict = None) -> dict | None:
    with get_engine().connect() as conn:
        result = conn.execute(text(query), params or {})
        keys = result.keys()
        row = result.fetchone()
        return dict(zip(keys, row)) if row else None

def execute(query: str, params: dict = None) -> None:
    with get_engine().connect() as conn:
        conn.execute(text(query), params or {})
        conn.commit()

def execute_returning(query: str, params: dict = None):
    with get_engine().connect() as conn:
        result = conn.execute(text(query), params or {})
        conn.commit()
        return result.fetchone()
