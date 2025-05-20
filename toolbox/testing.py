import logging
from contextlib import asynccontextmanager

import asyncpg

logger = logging.getLogger(__name__)


@asynccontextmanager
async def debug_client(app, app_path: str = "http://test"):
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=app_path,
    ) as client:
        yield client
        pass


@asynccontextmanager
async def temporary_database(settings: "DatabaseConnectionSettings", base_model, db_prefix: str = "test"):
    original_settings = settings.__class__(**settings.__dict__)
    test_db_name = f"{db_prefix}_{original_settings.POSTGRES_DB}"
    settings.POSTGRES_DB = test_db_name

    from toolbox.sqlalchemy.connection import DatabaseConnectionManager

    connection_factory = DatabaseConnectionManager(settings=original_settings)

    dsn = settings.get_dsn()
    try:
        conn = await asyncpg.connect(dsn=dsn)
    except:
        conn = await asyncpg.connect(dsn=dsn.replace(f"/{settings.POSTGRES_DB}", "/postgres"))
        await conn.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")

    async_engine = connection_factory.get_engine()
    async with async_engine.begin() as conn:
        await conn.run_sync(base_model.metadata.create_all)
        logger.debug({"msg": "Migration 'settings.POSTGRES_DB' was completed"})
        yield

        await conn.run_sync(base_model.metadata.drop_all)
