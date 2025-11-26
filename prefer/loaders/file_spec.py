import json
import os

import pytest

import prefer
from prefer.loaders import file as file_loader

FIXTURE_IDENTIFIER = "test.json"


def get_fixture_path(*args):
    return os.path.join(os.path.dirname(prefer.__file__), "fixtures", *args)


def simple_loader():
    return file_loader.FileLoader(
        configuration={
            "paths": [get_fixture_path()],
        },
    )


@pytest.mark.asyncio
async def test_FileLoader_provides_returns_True_for_file_urls_path():
    assert file_loader.FileLoader.provides(
        "file:///home/monokrome/.config/prefer/config.py",
    )


@pytest.mark.asyncio
async def test_FileLoader_provides_returns_True_as_fallback_if_url_not_given():
    assert file_loader.FileLoader.provides("config.py")


@pytest.mark.asyncio
async def test_FileLoader_provides_returns_False_for_non_file_urls():
    assert not file_loader.FileLoader.provides("https://github.com/monokrome")


@pytest.mark.asyncio
async def test_loader_locate_returns_expected_file_path():
    expectation = [get_fixture_path(FIXTURE_IDENTIFIER)]
    assert expectation == await simple_loader().locate(FIXTURE_IDENTIFIER)


@pytest.mark.asyncio
async def test_loader_locate_returns_detects_similar_files():
    expectation = [get_fixture_path(FIXTURE_IDENTIFIER)]
    result = await simple_loader().locate(FIXTURE_IDENTIFIER.split(".")[0])
    assert expectation == result


@pytest.mark.asyncio
async def test_loader_load_returns_LoadResult_of_file():
    result = await simple_loader().load(FIXTURE_IDENTIFIER)

    assert json.loads(result.content) == {
        "name": "Bailey",
        "roles": ["engineer", "wannabe musician"],
    }


@pytest.mark.asyncio
async def test_loader_load_returns_None_if_nothing_matches():
    result = await file_loader.FileLoader(
        configuration={"paths": ["."]},
    ).load(FIXTURE_IDENTIFIER)

    assert result is None


def test_read_returns_none_for_nonexistent_file():
    result = file_loader.read("/nonexistent/path/to/file.txt")
    assert result is None


@pytest.mark.asyncio
async def test_loader_locate_skips_nonexistent_paths():
    loader = file_loader.FileLoader(
        configuration={"paths": ["/nonexistent/path", get_fixture_path("")]}
    )
    result = await loader.locate(FIXTURE_IDENTIFIER)
    assert len(result) > 0
    assert all("/nonexistent/path" not in path for path in result)


@pytest.mark.asyncio
async def test_loader_locate_prefers_exact_match():
    """Test that exact file matches are preferred over extension matches."""
    loader = file_loader.FileLoader(
        configuration={"paths": [get_fixture_path("")]}
    )

    result = await loader.locate("test.json")
    expected = [get_fixture_path("test.json")]

    assert result == expected


@pytest.mark.asyncio
async def test_loader_locate_finds_all_matching_extensions():
    """Test that locate() finds files with all supported extensions."""
    loader = file_loader.FileLoader(
        configuration={"paths": [get_fixture_path("")]}
    )

    result = await loader.locate("json_test")
    found_extensions = {os.path.splitext(f)[1] for f in result}

    assert len(result) == 4
    assert ".json" in found_extensions
    assert ".yaml" in found_extensions
    assert ".ini" in found_extensions
    assert ".xml" in found_extensions


@pytest.mark.asyncio
async def test_loader_has_extension_detection():
    """Test the _has_extension helper method."""
    loader = file_loader.FileLoader()

    assert loader._has_extension("test.json") == True
    assert loader._has_extension("config.xml") == True
    assert loader._has_extension("settings.ini") == True

    assert loader._has_extension("test") == False
    assert loader._has_extension("config") == False
    assert loader._has_extension("settings") == False

    assert loader._has_extension(".hidden") == True
    assert loader._has_extension("path/to/file.json") == True
    assert loader._has_extension("path/to/file") == False


@pytest.mark.asyncio
async def test_loader_locate_with_nonexistent_identifier():
    """Test locate() with identifier that doesn't match any files."""
    loader = file_loader.FileLoader(
        configuration={"paths": [get_fixture_path("")]}
    )

    result = await loader.locate("nonexistent")

    assert result == []


@pytest.mark.asyncio
async def test_loader_locate_with_multiple_paths():
    """Test locate() with multiple search paths."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir1:
        with tempfile.TemporaryDirectory() as temp_dir2:
            test_file1 = os.path.join(temp_dir1, "example.json")
            test_file2 = os.path.join(temp_dir2, "example.xml")

            with open(test_file1, "w") as f:
                f.write('{"from": "dir1"}')

            with open(test_file2, "w") as f:
                f.write("<root><from>dir2</from></root>")

            loader = file_loader.FileLoader(
                configuration={"paths": [temp_dir1, temp_dir2]}
            )

            result = await loader.locate("example")

            assert len(result) >= 2
            assert any(path.endswith("example.json") for path in result)
            assert any(path.endswith("example.xml") for path in result)


@pytest.mark.asyncio
async def test_loader_locate_prevents_path_traversal():
    """Test that locate() prevents path traversal attacks."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        loader = file_loader.FileLoader(configuration={"paths": [temp_dir]})

        result = await loader.locate("../../../etc/passwd")

        assert result == []


@pytest.mark.asyncio
async def test_loader_locate_finds_file_with_extension_in_directory():
    """Test that locate() finds files when identifier has extension."""
    loader = file_loader.FileLoader(
        configuration={"paths": [get_fixture_path("")]}
    )

    result = await loader.locate("json_test.json")

    assert len(result) == 1
    assert result[0].endswith("json_test.json")
