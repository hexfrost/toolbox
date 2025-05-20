import pytest

from toolbox.sqlalchemy.connection import DatabaseConnectionSettings


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


@pytest.fixture(autouse=True)
async def temp_db(db_settings):
    from toolbox.testing import temporary_database
    from toolbox.sqlalchemy.models import BaseModel
    async with temporary_database(settings=db_settings, base_model=BaseModel):
        yield
        pass


