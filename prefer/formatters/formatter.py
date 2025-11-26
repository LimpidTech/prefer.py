import typing


def ensure_formatter_defines(method_name: str) -> typing.NoReturn:
    raise NotImplementedError(
        f'Object must define a "{method_name}" attribute, but it '
        "does not exist."
    )


class Formatter:
    def __init__(
        self, configuration: typing.Any | None = None
    ) -> None:
        self.configuration: typing.Any | None = configuration

    @classmethod
    def provides(cls, identifier: str) -> bool:
        return any(identifier.endswith(ext) for ext in cls.extensions())

    @staticmethod
    def extensions() -> set[str]:
        ensure_formatter_defines("extensions")

    async def serialize(self, source: dict[str, typing.Any]) -> str:
        ensure_formatter_defines("serialize")

    async def deserialize(self, source: str) -> dict[str, typing.Any]:
        ensure_formatter_defines("deserialize")
