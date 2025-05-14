import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from toolbox.database import DatabaseConnection, DatabaseConnectionManager


@pytest.fixture
def db_settings():
    class TestSettings(DatabaseConnection):
        POSTGRES_USER = "test_user"
        POSTGRES_PASSWORD = "test_password"
        POSTGRES_HOST = "test_host"
        POSTGRES_PORT = "5432"
        POSTGRES_DB = "test_db"

    return TestSettings


@pytest.fixture
def mock_engine():
    return MagicMock(spec=AsyncEngine)


@pytest.fixture(scope="function")
def database_connector(db_settings):
    dc = DatabaseConnectionManager(settings=db_settings)
    return dc


@pytest.mark.asyncio
async def test_database_manager_no_settings(database_connector):
    database_connector._settings = None
    database_connector._engine = None
    database_connector._async_sessionmaker = None

    with pytest.raises(RuntimeError, match="No settings available"):
        database_connector._get_settings()


def test_database_manager_set_engine(database_connector, mock_engine):
    database_connector.set_engine(mock_engine)
    assert database_connector._engine == mock_engine


@patch('toolbox.database.create_async_engine')
def test_database_manager_get_engine_creates_new(mock_create_engine, database_connector, db_settings):
    database_connector._engine = None

    expected_url = f"postgresql+asyncpg://{db_settings.POSTGRES_USER}:{db_settings.POSTGRES_PASSWORD}@{db_settings.POSTGRES_HOST}:{db_settings.POSTGRES_PORT}/{db_settings.POSTGRES_DB}"

    database_connector.get_engine()

    mock_create_engine.assert_called_once()
    call_args = mock_create_engine.call_args[0][0]
    assert call_args == expected_url


def test_database_manager_get_engine_returns_existing(database_connector, mock_engine):
    database_connector.set_engine(mock_engine)
    result = database_connector.get_engine()
    assert result == mock_engine


@patch('toolbox.database.async_sessionmaker')
def test_database_manager_get_session_maker(mock_sessionmaker, database_connector, mock_engine):
    database_connector.set_engine(mock_engine)
    database_connector._async_sessionmaker = None

    database_connector.get_session_maker()

    mock_sessionmaker.assert_called_once_with(
        mock_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )


def test_database_manager_get_session_maker_returns_existing(database_connector):
    mock_sessionmaker = MagicMock()
    database_connector._async_sessionmaker = mock_sessionmaker

    result = database_connector.get_session_maker()
    assert result == mock_sessionmaker
