# hexfrost-toolbox

Open source library with useful utils for fast development


## Installation

```bash
pip install hexfrost-toolbox
```

## Usage

### Auth Middleware (FastAPI)

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
