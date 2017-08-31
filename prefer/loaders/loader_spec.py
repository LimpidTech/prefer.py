import types
import functools
import pytest

from prefer.loaders import loader

MOCK_IDENTIFIER = 'Mock Identifier'


def raises_expected_exception(fn, *, kind: Exception=Exception):
    raised = False

    try:
        result = fn()

        if isinstance(result, types.GeneratorType):
            yield from result

    except kind:
        raised = True

    return raised


@pytest.mark.asyncio
async def test_Loader_provides_raises_NotImplementedError():
    test_fn = functools.partial(loader.Loader.provides, 'config')
    assert raises_expected_exception(test_fn, kind=NotImplementedError)


@pytest.mark.asyncio
async def test_Loader_locate_acts_as_an_identity_function():
    assert MOCK_IDENTIFIER is await loader.Loader().locate(MOCK_IDENTIFIER)


@pytest.mark.asyncio
async def test_Loader_load_raises_NotImplementedError():
    def load():
        return (yield from loader.Loader().load('config'))

    assert raises_expected_exception(load, kind=NotImplementedError)
