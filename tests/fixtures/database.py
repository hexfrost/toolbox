import pytest

from toolbox.sqlalchemy.connection import DatabaseConnectionSettings, DatabaseConnectionManager


@pytest.fixture(autouse=True)
def db_settings():
    from pydantic import BaseModel
    data = dict(
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD = "postgres",
        POSTGRES_HOST = "0.0.0.0",
        POSTGRES_PORT = "5432",
        POSTGRES_DB = "postgres"
    )
    class TestSettings(BaseModel, DatabaseConnectionSettings):
        pass

    return TestSettings(**data)


@pytest.fixture
async def database_test(db_settings):
    from toolbox.testing import temporary_database
    from toolbox.sqlalchemy.models import BaseModel
    async with temporary_database(settings=db_settings, base_model=BaseModel):
        yield
        pass


@pytest.fixture
async def database_connector(database_test, db_settings):
    dc = DatabaseConnectionManager(settings=db_settings)
    return dc
