import sys

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from prefer.formatters import toml

TOML_DATA = 'mock_config = {name = "Bailey"}\n'
REAL_DATA = tomllib.loads(TOML_DATA)

formatter = toml.TOMLFormatter()


@pytest.mark.asyncio
async def test_toml_formatter_provides_expected_file_extensions():
    assert toml.TOMLFormatter.provides("test.toml") is True


@pytest.mark.asyncio
async def test_toml_formatter_does_not_provide_unexpected_file_extensions():
    assert toml.TOMLFormatter.provides("test.bmp") is False
    assert toml.TOMLFormatter.provides("test.yaml") is False


@pytest.mark.asyncio
async def test_toml_formatter_serializes_to_toml():
    result = await formatter.serialize(REAL_DATA)
    assert tomllib.loads(result) == REAL_DATA


@pytest.mark.asyncio
async def test_toml_formatter_deserializes_from_toml():
    assert REAL_DATA == await formatter.deserialize(TOML_DATA)


@pytest.mark.asyncio
async def test_toml_formatter_raises_error_on_invalid_toml():
    invalid_toml = "invalid = [unclosed array"
    try:
        await formatter.deserialize(invalid_toml)
        assert False, "Should have raised an exception"
    except Exception:
        pass
