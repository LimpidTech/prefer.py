import typing
import yaml


class YAMLFormatter(object):
    @staticmethod
    def provides(identifier: str):
        return identifier.endswith('.yml') or identifier.endswith('.yaml')

    async def serialize(self, source: typing.Dict[str, typing.Any]) -> str:
        return yaml.dump(source)

    async def deserialize(self, source: str) -> typing.Dict[str, typing.Any]:
        return yaml.safe_load(source)
