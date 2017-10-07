import typing
from prefer import configuration


def ensure_formatter_defines(method_name: str):
    raise NotImplementedError(
        (
            'Object must define a "{method_name}" attribute, but it '
            'does not exist.'
        ).format(method_name=method_name)
    )


class Formatter:
    def __init__(self, configuration=configuration.Configuration):
        self.configuration = configuration

    @staticmethod
    def provides(identifier: str):
        return ensure_formatter_defines('provides')

    async def serialize(self, source: typing.Dict[str, typing.Any]) -> str:
        return ensure_formatter_defines('serialize')

    async def deserialize(self, source: str) -> typing.Dict[str, typing.Any]:
        return ensure_formatter_defines('deserialize')
