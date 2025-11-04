import pytest

from prefer.formatters import xml

XML_DATA = "<root><name>Bailey</name></root>"
REAL_DATA = {"root": {"name": {"$": "Bailey"}}}

formatter = xml.XMLFormatter()


@pytest.mark.asyncio
async def test_xml_formatter_provides_expected_file_extensions():
    assert xml.XMLFormatter.provides("test.xml") is True


@pytest.mark.asyncio
async def test_xml_formatter_does_not_provide_unexpected_file_extensions():
    assert xml.XMLFormatter.provides("test.json") is False
    assert xml.XMLFormatter.provides("test.yaml") is False


@pytest.mark.asyncio
async def test_xml_formatter_serializes_to_xml():
    result = await formatter.serialize(REAL_DATA)
    assert "<root>" in result
    assert "<name>Bailey</name>" in result


@pytest.mark.asyncio
async def test_xml_formatter_deserializes_from_xml():
    result = await formatter.deserialize(XML_DATA)
    assert "root" in result
    assert "name" in result["root"]
