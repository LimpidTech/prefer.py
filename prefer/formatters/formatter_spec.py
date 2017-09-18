import pytest

from prefer.formatters import formatter


@pytest.mark.asyncio
async def test_Formatter_provide_raises_NotImplementedError():
    caught_exception = False

    try:
        formatter.Formatter.provides(None)
    except NotImplementedError:
        caught_exception = True

    assert caught_exception


@pytest.mark.asyncio
async def test_Formatter_serialize_raises_NotImplementedError():
    caught_exception = False

    try:
        await formatter.Formatter().serialize({})
    except NotImplementedError:
        caught_exception = True

    assert caught_exception


@pytest.mark.asyncio
async def test_Formatter_deserialize_raises_NotImplementedError():
    caught_exception = False

    try:
        await formatter.Formatter().deserialize('{}')
    except NotImplementedError:
        caught_exception = True

    assert caught_exception
