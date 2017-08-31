import pytest
import unittest

import prefer


@pytest.mark.asyncio
async def test_load_loads_configuration_file():
    assert {} == await prefer.load('test.json')
