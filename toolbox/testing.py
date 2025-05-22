import asyncio
import logging
from contextlib import asynccontextmanager

import asyncpg

from toolbox.sqlalchemy.connection import DatabaseConnectionManager

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


class TemporaryDatabaseConnectionManager(DatabaseConnectionManager):
    # TODO: create database with included connections and options or creae one or many tables from sql model
    pass


@asynccontextmanager
async def temporary_database(settings: "DatabaseConnectionSettings", base_model, db_prefix: str = "test"):
    original_settings = settings.__class__(**settings.__dict__)
    test_db_name = f"{db_prefix}_{original_settings.POSTGRES_DB}"
    settings.POSTGRES_DB = test_db_name

    dsn = settings.get_dsn().replace(f"/{settings.POSTGRES_DB}", "/postgres")
    async with asyncio.Lock() as lock:
        try:
            conn = await asyncpg.connect(dsn=dsn)
            await conn.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")
            await conn.close()
        except Exception as e:
            logger.error({"mgs": e})
            await conn.close()

        db_manager = DatabaseConnectionManager(settings=settings)
        async with db_manager.get_db_session() as conn:
            try:
                await conn.run_sync(base_model.metadata.create_all)
            except Exception as e:
                logger.error({"msg": e})

        yield

    try:
        conn = await asyncpg.connect(dsn=dsn)
        await conn.execute(f"DROP DATABASE {settings.POSTGRES_DB}")
    except Exception as e:
        logger.error({"msg": e})
