from functools import cache

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool


class DatabaseConnection:
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str


class DatabaseConnectionManager:
    
    def __init__(self, settings: DatabaseConnection):
        self._engine = None
        self._async_sessionmaker = None
        self._settings = settings

    def _get_settings(self):
        if not self._settings:
            raise RuntimeError('No settings available')
        return self._settings

    def set_engine(self, engine: AsyncEngine):
        self._engine = engine

    def get_engine(self) -> AsyncEngine:
        if not self._engine:
            s = self._settings
            db_host = s.POSTGRES_HOST
            self._engine = create_async_engine(
                f"postgresql+asyncpg://{s.POSTGRES_USER}:{s.POSTGRES_PASSWORD}@{db_host}:{s.POSTGRES_PORT}/{s.POSTGRES_DB}",
                poolclass=NullPool,
            )
        return self._engine

    def get_session_maker(self):
        if not self._async_sessionmaker:
            self._async_sessionmaker = async_sessionmaker(
                self.get_engine(),
                expire_on_commit=False,
                class_=AsyncSession,
            )
        return self._async_sessionmaker


# TODO: add depends for fastapi
