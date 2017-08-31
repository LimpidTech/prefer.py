import pytest
import unittest
import yaml as yaml_native

from prefer.formatters import yaml

YAML_DATA = "mock_config: {name: Bailey}\n"
REAL_DATA = yaml_native.safe_load(YAML_DATA)

formatter = yaml.YAMLFormatter()


@pytest.mark.asyncio
async def test_yaml_formatter_provides_expected_file_extensions():
    assert yaml.YAMLFormatter.provides('test.yml') is True
    assert yaml.YAMLFormatter.provides('test.yaml') is True


@pytest.mark.asyncio
async def test_yaml_formatter_does_not_provide_unexpected_file_extensions():
    assert yaml.YAMLFormatter.provides('test.bmp') is False
    assert yaml.YAMLFormatter.provides('test.jpeg') is False


@pytest.mark.asyncio
async def test_yaml_formatter_serializes_to_yaml():
    assert YAML_DATA == await formatter.serialize(REAL_DATA)


@pytest.mark.asyncio
async def test_yaml_formatter_deserializes_from_yaml():
    assert REAL_DATA == await formatter.deserialize(YAML_DATA)
