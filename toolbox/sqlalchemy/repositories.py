from typing import Annotated

from sqlalchemy import select
from fastapi import Depends

from toolbox.sqlalchemy.connection import DatabaseConnectionManager
from toolbox.schemes import SensitiveDataScheme, BaseScheme

AnyPydanticModel = Annotated[BaseScheme, Depends(BaseScheme)]
AnySQLAlchemyModel = Annotated[BaseScheme, Depends(SensitiveDataScheme)]


class AbstractDatabaseCrudManager:
    _alchemy_model = type[AnySQLAlchemyModel]
    _pydantic_model = type[AnyPydanticModel]

    @classmethod
    async def add_one(cls, data_model: AnyPydanticModel) -> None:
        obj = cls._alchemy_model(**data_model.encrypt_fields().model_dump())
        connector = DatabaseConnectionManager()
        session = connector.get_session_maker()
        async with session() as conn:
            conn.add(obj)
            await conn.commit()
            await conn.refresh(obj)

    @classmethod
    async def get_all(cls, limit: int = 100, offset: int = 0):
        session = DatabaseConnectionManager.get_session_maker()
        async with session() as conn:
            query = select(cls._alchemy_model).limit(limit).offset(offset)
            result = [v[0] for v in (await conn.execute(query)).all()]
        return result