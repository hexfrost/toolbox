# `hexfrost-toolbox` - batteries for FastAPI projects

Open source library with useful utils for fast development


## Installation

```bash
pip install hexfrost-toolbox
```

## Usage

### Test Client

```python
from toolbox.testing import debug_client

app = FastAPI()

async with debug_client(app) as client:
    response = await client.get('/')
    assert response.status_code == 200
```
You can use app with this client for debug code like as `django.testclient`


### Test Database

The function will create a new database with a prefix next to the one specified in the settings.


* The original settings file will be overwritten so that in all tests queries will go to the new database.

```python
POSTGRES_DB = "postgres" # will overwrite -> "test_postgres"
```

You can use one database settings file for all tests, without worrying that the original database will be overwritten

```python
from toolbox.testing import temporary_database
from toolbox.sqlalchemy.connection import DatabaseConnectionSettings

from your_project.alchemy_models import BaseModel


@pytest.fixture(autouse=True)
def db_settings():
    data = DatabaseConnectionSettings(
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD = "postgres",
        POSTGRES_HOST = "0.0.0.0",
        POSTGRES_PORT = "5432",
        POSTGRES_DB = "postgres"
    )

    return data

@pytest.fixture(autouse=True)
async def temp_db(db_settings):
    async with temporary_database(
            settings=db_settings,
            base_model=BaseModel,
            # db_prefix = "test" # optional
    ):
        yield
        pass
```

### Database Connect

```python
from fastapi import Depends, FastAPI
from toolbox.sqlalchemy.connection import DatabaseConnectionManager, DatabaseConnectionSettings


settings = DatabaseConnectionSettings(
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD = "postgres",
        POSTGRES_HOST = "0.0.0.0",
        POSTGRES_PORT = "5432",
        POSTGRES_DB = "postgres"
    )

get_db_conn = DatabaseConnectionManager(settings=settings)

app = FastAPI()

@app.get("/")
async def index(database_conn = Depends(get_db_conn)):
    ...
```

### Auth Middleware
#### FastAPI

```python

from toolbox.auth.middlewares.fastapi_ import BearerTokenMiddleware, BearerTokenMiddlewareSettings

class TokenStorage:

    async def __call__(self, token: str) -> bool:
        ...

token_validator = TokenStorage()
settings = BearerTokenMiddlewareSettings(
    token_validator=token_validator,
    exclude_paths=["/docs"]
)

BearerTokenMiddleware.set_settings(settings)

app = FastAPI()
app.add_middleware(BearerTokenMiddleware)

```

### Tools



That's it! Enjoy! 🚀
