import asyncio
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Callable, TypeVar

try:
    from icecream import ic
except ImportError:
    pass

T = TypeVar('T')


def asyncio_run(func: T) -> T:
    # get last frame_info
    frame_info = inspect.stack()[1]

    name = frame_info.frame.f_globals['__name__']
    # ic(name)

    if name == '__main__':
        filename = frame_info.filename
        # ic(filename)

        spec = importlib.util.spec_from_file_location(
            Path(filename).stem,
            filename
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        main = getattr(module, func.__name__)
        asyncio.run(main())
    else:
        return func
