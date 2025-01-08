# hexfrost-toolbox

Open source library with useful utils for fast development


## Installation

```bash
pip install hexfrost-toolbox
```

## Usage


### Create async generator from list

```python
from toolbox import create_async_generator


async def main():
    urls = ['https://example.com', 'https://example2.com']
    
    async_iterable = create_async_generator(urls)
    
    async for url in async_iterable:
        await do_something(url)

```

### Create async function from sync function

```python
from toolbox import sync_to_async

def some_blocking_function():
    return 'Hello, World!'

async def main():
    async_function = sync_to_async(some_blocking_function)
    
    result = await async_function()
    
    print(result)

```

### Create sync function from async function

```python
from toolbox import async_to_sync

async def some_async_function():
    return 'Hello, World!'

def main():
    sync_function = async_to_sync(some_async_function)
    
    result = sync_function()
    
    print(result)

```

That's it! Enjoy! 🚀


