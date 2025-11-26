import configparser
import io
import typing

from prefer.formatters import formatter


class INIFormatter(formatter.Formatter):
    @staticmethod
    def extensions() -> set[str]:
        return {".ini", ".cfg"}

    async def serialize(self, source: dict[str, typing.Any]) -> str:
        config = configparser.ConfigParser()
        for section, values in source.items():
            if not isinstance(values, dict):
                raise ValueError("INI sections must be dictionaries")

            config[section] = values
        output = io.StringIO()
        config.write(output)
        return output.getvalue()

    async def deserialize(self, source: str) -> dict[str, typing.Any]:
        config = configparser.ConfigParser()
        config.read_string(source)
        result: dict[str, typing.Any] = {
            section: dict(config[section]) for section in config.sections()
        }
        return result
