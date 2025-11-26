import typing
import xml.etree.ElementTree as ET

import xmljson

from prefer.formatters import formatter


class XMLFormatter(formatter.Formatter):
    @staticmethod
    def extensions() -> set[str]:
        return {".xml"}

    async def serialize(self, source: typing.Dict[str, typing.Any]) -> str:
        elem = xmljson.badgerfish.etree(source)
        if isinstance(elem, list):
            elem = elem[0]
        return ET.tostring(elem, encoding="unicode")

    async def deserialize(self, source: str) -> typing.Dict[str, typing.Any]:
        elem = ET.fromstring(source)
        result: typing.Dict[str, typing.Any] = xmljson.badgerfish.data(elem)
        return result
