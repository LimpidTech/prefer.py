import os

import pytest

import prefer


@pytest.mark.asyncio
async def test_load_loads_configuration_file():
    configurator = await prefer.load(
        os.path.join(
            'prefer',
            'fixtures',
            'test.json',
        )
    )

    assert configurator.context == {
        'name': 'Bailey',
        'roles': [
            'engineer',
            'wannabe musician',
        ],
    }
