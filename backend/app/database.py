import ssl

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

_is_local = any(h in settings.DATABASE_URL for h in ("localhost", "127.0.0.1"))
_connect_args = {} if _is_local else {"ssl": ssl.create_default_context()}

engine = create_async_engine(settings.DATABASE_URL, echo=False, connect_args=_connect_args)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
