from sqlalchemy import select

from tests.fixtures.database import database_connector


async def test_fastapi_depends_itegration_test_2(database_connector):
    from fastapi import Depends, FastAPI
    app = FastAPI()
    @app.get("/")
    async def index(database_conn = Depends(database_connector)):
        async with database_conn:
            res = await database_conn.scalar(select(1))
        return {"status": "ok"}

    from toolbox.testing import debug_client
    async with debug_client(app) as client:
        response1 = await client.get('/')
        assert response1.status_code == 200