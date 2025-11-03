import typing

if typing.TYPE_CHECKING:
    pass


def ensure_formatter_defines(method_name: str) -> typing.NoReturn:
    raise NotImplementedError(
        f'Object must define a "{method_name}" attribute, but it '
        "does not exist."
    )


class Formatter:
    def __init__(
        self, configuration: typing.Optional[typing.Any] = None
    ) -> None:
        self.configuration: typing.Optional[typing.Any] = configuration

    @staticmethod
    def provides(identifier: str) -> bool:
        ensure_formatter_defines("provides")

    async def serialize(self, source: typing.Dict[str, typing.Any]) -> str:
        ensure_formatter_defines("serialize")

    async def deserialize(self, source: str) -> typing.Dict[str, typing.Any]:
        ensure_formatter_defines("deserialize")
