import configparser
import io
import typing

from prefer.formatters import formatter


class INIFormatter(formatter.Formatter):
    @staticmethod
    def provides(identifier: str) -> bool:
        return identifier.endswith(".ini") or identifier.endswith(".cfg")

    async def serialize(self, source: typing.Dict[str, typing.Any]) -> str:
        config = configparser.ConfigParser()
        for section, values in source.items():
            config[section] = values
        output = io.StringIO()
        config.write(output)
        return output.getvalue()

    async def deserialize(self, source: str) -> typing.Dict[str, typing.Any]:
        config = configparser.ConfigParser()
        config.read_string(source)
        result: typing.Dict[str, typing.Any] = {
            section: dict(config[section]) for section in config.sections()
        }
        return result
