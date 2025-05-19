from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from toolbox.sqlalchemy.connection import DatabaseConnectionSettings, DatabaseConnectionManager


@pytest.fixture
def db_settings():
    class TestSettings(DatabaseConnectionSettings):
        POSTGRES_USER = "postgres"
        POSTGRES_PASSWORD = "postgres"
        POSTGRES_HOST = "0.0.0.0"
        POSTGRES_PORT = "5432"
        POSTGRES_DB = "test_postgres"

    return TestSettings


@pytest.fixture
def mock_engine():
    return MagicMock(spec=AsyncEngine)


@pytest.fixture(scope="function")
def database_connector(db_settings):
    dc = DatabaseConnectionManager(settings=db_settings)
    return dc
