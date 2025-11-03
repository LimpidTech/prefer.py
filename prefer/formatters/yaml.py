import typing

import yaml

from prefer.formatters import formatter


class YAMLFormatter(formatter.Formatter):
    @staticmethod
    def provides(identifier: str) -> bool:
        return identifier.endswith(".yml") or identifier.endswith(".yaml")

    async def serialize(self, source: typing.Dict[str, typing.Any]) -> str:
        result: str = yaml.dump(source)
        return result

    async def deserialize(self, source: str) -> typing.Dict[str, typing.Any]:
        result: typing.Dict[str, typing.Any] = yaml.safe_load(source)
        return result
