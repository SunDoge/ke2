import asyncio
import re
import shlex
import sys
from asyncio import subprocess
from typing import Any, Union

try:
    from icecream import ic
except ImportError:
    pass

# class ShlexFormatter(Formatter):


#     def get_value(self, key: Union[int, str], args: Sequence[Any], kwargs: Mapping[str, Any]) -> Any:
#         args
#         return super().get_value(key, args, kwargs)


class ProcessOutput:

    def __init__(
        self,
        stdout: str,
        stderr: str,
        returncode: int,
    ) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def __str__(self) -> str:
        return self.stdout

    def __format__(self, format_spec: str) -> str:
        if format_spec == '!r':
            return substitute(self)
        else:
            return str(self)


class ProcessFutureParallel:

    def __init__(self, process_futures: list, verbose: bool = True) -> None:
        self.process_futures = process_futures
        self.verbose = verbose

    def __floordiv__(self, other) -> 'ProcessFutureParallel':
        self.process_futures.append(other)
        return self

    async def _call(self):
        return await asyncio.gather(*self.process_futures)

    def __await__(self):
        return self._call().__await__()

    def __rshift__(self, cmd: str) -> 'ProcessFutureParallel':
        self.process_futures.append(ProcessFuture(cmd, self.verbose))
        return self


class ProcessFuture:

    def __init__(self, cmd: str, verbose: bool) -> None:
        if verbose:
            print(f'$ {colorize(cmd)}')

        self.cmd = cmd
        self.verbose = verbose
        self.task = self._create_task()

    async def _call(self):
        proc = await subprocess.create_subprocess_shell(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout_data, stderr_data = await proc.communicate()

        if self.verbose:
            sys.stdout.buffer.write(stdout_data)
            sys.stdout.buffer.flush()
        stdout = stdout_data.decode()

        if self.verbose:
            sys.stdout.buffer.write(stderr_data)
            sys.stdout.buffer.flush()
        stderr = stderr_data.decode()

        output = ProcessOutput(
            stdout,
            stderr,
            proc.returncode,
        )
        return output

    def __await__(self):
        # return self._call().__await__()
        return self.task.__await__()

    def _create_task(self):
        task = asyncio.create_task(self._call())
        return task

    def __rshift__(self, cmd: Union[str, 'ProcessFuture']) -> ProcessFutureParallel:
        if isinstance(cmd, str):
            fut = ProcessFuture(cmd, self.verbose)
        else:
            fut = cmd
        return ProcessFutureParallel([self, fut])


class Shell:

    def __init__(
        self,
        verbose: bool = True,
    ) -> None:
        self.verbose = verbose

    def __rshift__(self, cmd: str) -> ProcessFuture:
        return ProcessFuture(cmd, self.verbose)


def substitute(arg: Any) -> str:
    if isinstance(arg, ProcessOutput):
        return re.sub(r'\n$', '', arg.stdout)
    else:
        return str(arg)


def quote(x) -> str:
    return shlex.quote(substitute(x))


def colorize(cmd: str) -> str:
    return re.sub(
        r'^\w+(\s|$)',
        lambda m: green_bright(m.group(0)),
        cmd
    )


def green_bright(text: str) -> str:
    return f'\u001B[92m{text}\u001B[39m'


if __name__ == '__main__':
    print(green_bright('test green bright'))
