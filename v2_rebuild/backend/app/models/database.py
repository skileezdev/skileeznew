from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

# Production-ready database config
# Uses DATABASE_URL (for Postgres) if available, otherwise falls back to local SQLite
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

if SQLALCHEMY_DATABASE_URL:
    if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif SQLALCHEMY_DATABASE_URL.startswith("prisma+postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("prisma+postgres://", "postgresql+asyncpg://", 1)
else:
    SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./skileez_v2.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        yield session
