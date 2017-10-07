import json
import os
import prefer
import pytest

from prefer.loaders import file as file_loader

FIXTURE_IDENTIFIER = 'test.json'


def get_fixture_path(*args):
    return os.path.join(os.path.dirname(prefer.__file__), 'fixtures', *args)


def simple_loader():
    return file_loader.FileLoader(
        configuration={
            'paths': [get_fixture_path()],
        },
    )


@pytest.mark.asyncio
async def test_FileLoader_provides_returns_True_for_file_urls_path():
    assert file_loader.FileLoader.provides(
        'file:///home/monokrome/.config/prefer/config.py',
    )


@pytest.mark.asyncio
async def test_FileLoader_provides_returns_True_as_fallback_if_url_not_given():
    assert file_loader.FileLoader.provides('config.py')


@pytest.mark.asyncio
async def test_FileLoader_provides_returns_False_for_non_file_urls():
    assert not file_loader.FileLoader.provides('https://github.com/monokrome')


@pytest.mark.asyncio
async def test_loader_locate_returns_expected_file_path():
    expectation = [get_fixture_path(FIXTURE_IDENTIFIER)]
    assert expectation == await simple_loader().locate(FIXTURE_IDENTIFIER)


@pytest.mark.asyncio
async def test_loader_locate_returns_detects_similar_files():
    expectation = [get_fixture_path(FIXTURE_IDENTIFIER)]
    result = await simple_loader().locate(FIXTURE_IDENTIFIER.split('.')[0])
    assert expectation == result


@pytest.mark.asyncio
async def test_loader_load_returns_LoadResult_of_file():
    result = await simple_loader().load(FIXTURE_IDENTIFIER)

    assert json.loads(result.content) == {
        'name': 'Bailey',
        'roles': ['engineer', 'wannabe musician']
    }


@pytest.mark.asyncio
async def test_loader_load_returns_None_if_nothing_matches():
    result = await file_loader.FileLoader(
        configuration={'paths': ['.']},
    ).load(FIXTURE_IDENTIFIER)

    assert result is None
