import typing

import yaml

from prefer.formatters import formatter


class YAMLFormatter(formatter.Formatter):
    @staticmethod
    def extensions() -> set[str]:
        return {".yml", ".yaml"}

    async def serialize(self, source: dict[str, typing.Any]) -> str:
        result: str = yaml.dump(source)
        return result

    async def deserialize(self, source: str) -> dict[str, typing.Any]:
        result: dict[str, typing.Any] = yaml.safe_load(source)
        return result
