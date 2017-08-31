import json as json_native
import pytest

from prefer.formatters import json

JSON_DATA = '{"mock_config": {"name": "Bailey"}}'
REAL_DATA = json_native.loads(JSON_DATA)

formatter = json.JSONFormatter()


@pytest.mark.asyncio
async def test_json_native_formatter_provides_expected_file_extensions():
    assert json.JSONFormatter.provides('test.json') is True


@pytest.mark.asyncio
async def test_json_native_formatter_does_not_provide_unexpected_file_extensions(
):
    assert json.JSONFormatter.provides('test.bmp') is False
    assert json.JSONFormatter.provides('test.jpeg') is False


@pytest.mark.asyncio
async def test_json_formatter_serializes_to_json():
    assert JSON_DATA == await formatter.serialize(REAL_DATA)


@pytest.mark.asyncio
async def test_json_formatter_deserializes_from_json():
    assert REAL_DATA == await formatter.deserialize(JSON_DATA)
