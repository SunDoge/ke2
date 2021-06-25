from asyncio import subprocess


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


class ProcessFuture:

    def __init__(self, cmd: str) -> None:
        self.cmd = cmd

    async def _call(self):
        proc = await subprocess.create_subprocess_shell(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        output = ProcessOutput(
            stdout.decode(),
            stderr.decode(),
            proc.returncode,
        )
        return output

    
    def __await__(self):
        return self._call().__await__()


class Shell:

    def __init__(self) -> None:
        pass

    def __gt__(self, cmd: str) -> ProcessFuture:
        return ProcessFuture(cmd)


async def main():
    sh = Shell()
    output = await (sh > 'cat pyproject.toml')
    print(output)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
