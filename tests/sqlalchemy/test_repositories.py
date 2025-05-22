import pytest
from sqlalchemy import Column, Integer, String, orm

from toolbox.schemes import SensitiveDataScheme
from toolbox.sqlalchemy.connection import DatabaseConnectionManager, DatabaseConnectionSettings
from toolbox.sqlalchemy.repositories import AbstractDatabaseCrudManager


class BaseDatabaseModel(orm.DeclarativeBase):
    pass

class TestSQLAlchemyModel(BaseDatabaseModel):
    __tablename__ = "test_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sensitive_field = Column(String)


class TestPydanticModel(SensitiveDataScheme):
    _sensitive_fields = ["sensitive_field"]

    name: str
    sensitive_field: str


class TestItemRepository(AbstractDatabaseCrudManager):
    _alchemy_model = TestSQLAlchemyModel
    _pydantic_model = TestPydanticModel


@pytest.fixture(autouse=True, scope="session")
def db_settings():
    data = DatabaseConnectionSettings(
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD = "postgres",
        POSTGRES_HOST = "0.0.0.0",
        POSTGRES_PORT = "5432",
        POSTGRES_DB = "postgres"
    )
    return data


@pytest.fixture(autouse=True, scope="session")
async def temp_db(db_settings):
    from toolbox.testing import temporary_database
    from toolbox.sqlalchemy.models import BaseDatabaseModel
    async with temporary_database(settings=db_settings, base_model=BaseDatabaseModel) as db_connection:
        yield db_connection
        pass


@pytest.fixture(autouse=True, scope="session")
def database_connection(db_settings):
    dc = DatabaseConnectionManager(settings=db_settings)
    return dc


async def test_add_one_sensitive_field(temp_db, database_connection):

    new_obj = TestPydanticModel(
        name="test_item",
        sensitive_field="test_sensitive_field"
    )
    async with database_connection.get_db_session() as conn:
        from sqlalchemy.schema import CreateTable
        await conn.execute(CreateTable(TestSQLAlchemyModel.__table__))

        all_ = await TestItemRepository.get_all(conn)
        assert len(all_) == 0

        await TestItemRepository.add_one(conn, new_obj)

        all_ = await TestItemRepository.get_all(conn)
        assert len(all_) == 1
        assert all_[0].sensitive_field == "test_sensitive_field"
