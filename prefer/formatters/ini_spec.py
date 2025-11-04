import pytest

from prefer.formatters import ini

INI_DATA = """[mock_config]
name = Bailey

"""
REAL_DATA = {"mock_config": {"name": "Bailey"}}

formatter = ini.INIFormatter()


@pytest.mark.asyncio
async def test_ini_formatter_provides_expected_file_extensions():
    assert ini.INIFormatter.provides("test.ini") is True
    assert ini.INIFormatter.provides("test.cfg") is True


@pytest.mark.asyncio
async def test_ini_formatter_does_not_provide_unexpected_file_extensions():
    assert ini.INIFormatter.provides("test.json") is False
    assert ini.INIFormatter.provides("test.yaml") is False


@pytest.mark.asyncio
async def test_ini_formatter_serializes_to_ini():
    result = await formatter.serialize(REAL_DATA)
    assert "[mock_config]" in result
    assert "name = Bailey" in result


@pytest.mark.asyncio
async def test_ini_formatter_deserializes_from_ini():
    result = await formatter.deserialize(INI_DATA)
    assert result == REAL_DATA
