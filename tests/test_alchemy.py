import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy import select, String
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql.selectable import Select

from toolbox.sqlalchemy.repositories import AbstractDatabaseCrudManager
from toolbox.sqlalchemy.models import BaseModel
from toolbox.schemes import BaseScheme, SensitiveDataScheme


class TestPydanticModel(BaseScheme):
    name: str
    value: str

    def encrypt_fields(self):
        return self


class TestSQLAlchemyModel(BaseModel):
    __tablename__ = "test_table"
    name: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String)


class TestCrudManager(AbstractDatabaseCrudManager):
    _alchemy_model = TestSQLAlchemyModel
    _pydantic_model = TestPydanticModel


@pytest.fixture
def test_data():
    return TestPydanticModel(name="test_name", value="test_value")


@pytest.fixture
def mock_session():
    session = AsyncMock()

    async_context_manager_mock = AsyncMock()

    async_context_manager_mock.__aenter__.return_value = session

    async_context_manager_mock.__aexit__.return_value = False

    session_maker = MagicMock()
    session_maker.return_value = async_context_manager_mock

    return session_maker, session


@pytest.mark.asyncio
@patch('toolbox.sqlalchemy.connection.DatabaseConnectionManager')
async def test_add_one(mock_db_manager, mock_session, test_data):
    session_maker, session = mock_session
    await TestCrudManager.add_one(session, test_data)

    session.add.assert_called_once()
    added_model = session.add.call_args[0][0]
    assert isinstance(added_model, TestSQLAlchemyModel)
    assert added_model.name == test_data.name
    assert added_model.value == test_data.value

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(added_model)


@pytest.mark.asyncio
@patch('toolbox.sqlalchemy.connection.DatabaseConnectionManager')
async def test_get_all(mock_db_manager, mock_session):
    session_maker, session = mock_session

    test_models = [
        TestSQLAlchemyModel(name="test1", value="value1"),
        TestSQLAlchemyModel(name="test2", value="value2")
    ]

    db_operation_result_mock = MagicMock()
    db_operation_result_mock.all.return_value = [(model,) for model in test_models]

    session.execute.return_value = db_operation_result_mock

    result = await TestCrudManager.get_all(session, limit=10, offset=0)

    session.execute.assert_called_once()
    query = session.execute.call_args[0][0]
    assert isinstance(query, Select)

    assert len(result) == 2
    assert all(isinstance(item, TestSQLAlchemyModel) for item in result)
    assert result == test_models


@pytest.mark.asyncio
@patch('toolbox.sqlalchemy.connection.DatabaseConnectionManager')
async def test_get_all_with_custom_limit_offset(mock_db_manager, mock_session):
    session_maker, session = mock_session

    db_operation_result_mock = MagicMock()
    db_operation_result_mock.all.return_value = []
    session.execute.return_value = db_operation_result_mock

    await TestCrudManager.get_all(session, limit=5, offset=10)

    session.execute.assert_called_once()
    query = session.execute.call_args[0][0]

    assert query._limit_clause is not None
    assert query._limit_clause.value == 5
    assert query._offset_clause is not None
    assert query._offset_clause.value == 10


@pytest.mark.asyncio
@patch('toolbox.sqlalchemy.connection.DatabaseConnectionManager')
async def test_get_all_empty_result(mock_db_manager, mock_session):
    session_maker, session = mock_session

    execute_result = MagicMock()
    execute_result.all.return_value = []
    session.execute.return_value = execute_result

    result = await TestCrudManager.get_all(session)

    assert result == []
    session.execute.assert_called_once()
