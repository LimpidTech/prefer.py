import functools
import pytest

from prefer.formatters import formatter


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
async def test_Formatter_provide_raises_NotImplementedError():
    test_fn = functools.partial(formatter.Formatter.provides, None)
    assert raises_expected_exception(test_fn, kind=NotImplementedError)


@pytest.mark.asyncio
async def test_Formatter_serialize_raises_NotImplementedError():
    test_fn = functools.partial(formatter.Formatter().serialize, {})
    assert raises_expected_exception(test_fn, kind=NotImplementedError)


@pytest.mark.asyncio
async def test_Formatter_deserialize_raises_NotImplementedError():
    test_fn = functools.partial(formatter.Formatter().deserialize, '{}')
    assert raises_expected_exception(test_fn, kind=NotImplementedError)
