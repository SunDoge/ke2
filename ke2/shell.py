from asyncio import subprocess
import sys
from icecream import ic
import shlex
from string import Formatter
from typing import Union, Sequence, Mapping, Any
import inspect
import re


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


class ProcessFutureParallel:

    def __init__(self, process_futures: list) -> None:
        self.process_futures = process_futures

    def __floordiv__(self, other) -> 'ProcessFutureParallel':
        self.process_futures.append(other)
        return self

    async def _call(self):
        return await asyncio.gather(*self.process_futures)

    def __await__(self):
        return self._call().__await__()


class ProcessFuture:

    def __init__(self, cmd: str, verbose: bool) -> None:
        self.cmd = cmd
        self.verbose = verbose

    async def _call(self):
        proc = await subprocess.create_subprocess_shell(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout_data, stderr_data = await proc.communicate()

        if self.verbose:
            sys.stdout.buffer.write(stdout_data)
        stdout = stdout_data.decode()

        if self.verbose:
            sys.stdout.buffer.write(stderr_data)
        stderr = stderr_data.decode()

        output = ProcessOutput(
            stdout,
            stderr,
            proc.returncode,
        )
        return output

    def __await__(self):
        return self._call().__await__()

    def __floordiv__(self, other) -> ProcessFutureParallel:
        return ProcessFutureParallel([self, other])


class Shell:

    def __init__(
        self,
        verbose: bool = True,
    ) -> None:
        self.verbose = verbose

    # def __gt__(self, cmd: str) -> ProcessFuture:
    #     frame_info = inspect.stack()[1]
    #     local_vars = frame_info.frame.f_locals

    #     cmd_formatted = ShlexFormatter(local_vars).format(cmd)

    #     if self.verbose:
    #         print(f'$ {cmd_formatted}')

    #     return ProcessFuture(cmd_formatted, self.verbose)

    def __call__(self, cmd: str, *args: Any, **kwds: Any) -> ProcessFuture:

        new_args = (shlex.quote(substitute(x)) for x in args)
        new_kwds = {k: shlex.quote(substitute(v)) for k, v in kwds.items()}

        cmd_formatted = Formatter().format(cmd, *new_args, **new_kwds)

        if self.verbose:
            print(f'$ {cmd_formatted}')

        return ProcessFuture(cmd_formatted, self.verbose)


def substitute(arg) -> str:
    if isinstance(arg, ProcessOutput):
        return re.sub(r'\n$', '', arg.stdout)
    else:
        return str(arg)


def colorize(cmd: str) -> str:
    pass


async def main():
    sh = Shell()
    await sh('cat pyproject.toml | grep name')
    branch = await sh('git branch --show-current')
    await sh('echo branch is {branch}', branch=branch)

    await (
        sh('sleep 1; echo 1')
        // sh('sleep 2; echo 2')
        // sh('sleep 3; echo 3')
    )

    name = 'foo bar'
    await sh('mkdir /tmp/{name}', name=name)
    await sh('ls /tmp | grep {name}', name=name)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
