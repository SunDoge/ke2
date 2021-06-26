# Ke2

## Usage

```python
from ke2.prelude import *


@asyncio_run
async def main():
    await (sh >> 'cat pyproject.toml | grep name')
    branch = sh >> 'git branch --show-current'
    await (sh >> f'echo branch is {await branch:!r}')

    await (
        sh >> 'sleep 1; echo 1'
        >> 'sleep 2; echo 2'
        >> 'sleep 3; echo 3'
    )
    name = 'foo bar'
    await (sh >> f'mkdir /tmp/{name!r}')
    await (sh >> f'ls /tmp | grep {name!r}')
```

