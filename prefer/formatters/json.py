import typing

import json5

from prefer.formatters import formatter


class JSONFormatter(formatter.Formatter):
    @staticmethod
    def provides(identifier: str) -> bool:
        return identifier.endswith(".json") or identifier.endswith(".json5")

    async def serialize(self, source: typing.Dict[str, typing.Any]) -> str:
        result: str = json5.dumps(source, quote_keys=True)
        return result

    async def deserialize(self, source: str) -> typing.Dict[str, typing.Any]:
        result: typing.Dict[str, typing.Any] = json5.loads(source)
        return result
