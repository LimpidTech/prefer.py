import typing
import json

from prefer.formatters import formatter


class JSONFormatter(formatter.Formatter):
    @staticmethod
    def provides(identifier: str):
        return identifier.endswith('.json')

    async def serialize(self, source: typing.Dict[str, typing.Any]) -> str:
        return json.dumps(source)

    async def deserialize(self, source: str) -> typing.Dict[str, typing.Any]:
        return json.loads(source)
