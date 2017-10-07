import types
import pytest

from prefer.loaders import loader

MOCK_IDENTIFIER = 'Mock Identifier'


@pytest.mark.asyncio
async def test_Loader_provides_raises_NotImplementedError():
    caught_exception = False

    try:
        loader.Loader().provides('config')
    except NotImplementedError:
        caught_exception = True

    assert caught_exception


@pytest.mark.asyncio
async def test_Loader_locate_acts_as_an_identity_function():
    assert MOCK_IDENTIFIER is await loader.Loader().locate(MOCK_IDENTIFIER)


@pytest.mark.asyncio
async def test_Loader_load_raises_NotImplementedError():
    caught_exception = False

    try:
        await loader.Loader().load('config')
    except NotImplementedError:
        caught_exception = True

    assert caught_exception


@pytest.mark.asyncio
async def test_Loader_assigns_paths_based_on_configuration():
    paths = ['.']
    configuration = {'paths': paths}

    assert paths == loader.Loader(configuration=configuration).paths
