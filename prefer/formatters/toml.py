import sys
import typing

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # pragma: no cover

import tomli_w

from prefer.formatters import formatter


class TOMLFormatter(formatter.Formatter):
    @staticmethod
    def extensions() -> set[str]:
        return {".toml"}

    async def serialize(self, source: dict[str, typing.Any]) -> str:
        result: str = tomli_w.dumps(source)
        return result

    async def deserialize(self, source: str) -> dict[str, typing.Any]:
        result: dict[str, typing.Any] = tomllib.loads(source)
        return result
