import os

import pytest

import prefer

MOCK_CONFIGURATION_OBJECT = {"mock": "configuration"}


@pytest.mark.asyncio
async def test_load_loads_configuration_file():
    configurator = await prefer.load(
        os.path.join(
            "prefer",
            "fixtures",
            "test.json",
        )
    )

    assert configurator.context == {
        "name": "Bailey",
        "roles": [
            "engineer",
            "wannabe musician",
        ],
    }


@pytest.mark.asyncio
async def test_load_provides_configuration_to_loader():
    loaders = {"prefer.loaders.file:FileLoader": MOCK_CONFIGURATION_OBJECT}

    identifier = os.path.join("prefer", "fixtures", "test.json")

    configurator = await prefer.load(
        identifier,
        configuration={"loaders": loaders},
    )

    assert configurator.loader.configuration == MOCK_CONFIGURATION_OBJECT


@pytest.mark.asyncio
async def test_load_provides_configuration_to_formatter():
    formatters = {
        "prefer.formatters.json:JSONFormatter": MOCK_CONFIGURATION_OBJECT,
    }

    identifier = os.path.join("prefer", "fixtures", "test.json")

    configurator = await prefer.load(
        identifier,
        configuration={"formatters": formatters},
    )

    assert configurator.formatter.configuration == MOCK_CONFIGURATION_OBJECT


@pytest.mark.asyncio
async def test_load_handles_no_matching_formatter():
    identifier = os.path.join("prefer", "fixtures", "test.unknown")

    try:
        await prefer.load(identifier)
        assert False, "Should have raised an error for unknown format"
    except (AttributeError, TypeError, ValueError):
        pass


@pytest.mark.asyncio
async def test_load_handles_no_matching_loader():
    identifier = "http://example.com/config.json"

    try:
        await prefer.load(identifier)
        assert False, "Should have raised an error for unsupported protocol"
    except (AttributeError, TypeError, ValueError):
        pass
