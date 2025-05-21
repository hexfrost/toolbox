from sqlalchemy import select

from tests.fixtures.database import temp_db, db_settings
from tests.fixtures.db_connect import database_connector


async def test_fastapi_depends_itegration_test(temp_db, db_settings, database_connector):

    from fastapi import Depends, FastAPI
    app = FastAPI()
    @app.get("/")
    async def index(database_conn = Depends(database_connector)):
        await database_conn.scalar(select(1))
        return {"status": "ok"}

    from toolbox.testing import debug_client
    async with debug_client(app) as client:
        response1 = await client.get('/')
        assert response1.status_code == 200


async def test_debug_client_negative_test(temp_db, db_settings, database_connector):

    from fastapi import FastAPI
    app = FastAPI()

    from toolbox.testing import debug_client
    async with debug_client(app) as client:
        response1 = await client.get('/')
        assert response1.status_code == 404
