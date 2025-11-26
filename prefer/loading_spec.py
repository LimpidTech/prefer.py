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
async def test_load_provides_options_to_loader():
    loaders = {"prefer.loaders.file:FileLoader": MOCK_CONFIGURATION_OBJECT}

    identifier = os.path.join("prefer", "fixtures", "test.json")

    configurator = await prefer.load(
        identifier,
        options={"loaders": loaders},
    )

    assert configurator.loader.configuration == MOCK_CONFIGURATION_OBJECT


@pytest.mark.asyncio
async def test_load_provides_options_to_formatter():
    formatters = {
        "prefer.formatters.json:JSONFormatter": MOCK_CONFIGURATION_OBJECT,
    }

    identifier = os.path.join("prefer", "fixtures", "test.json")

    configurator = await prefer.load(
        identifier,
        options={"formatters": formatters},
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


@pytest.mark.asyncio
async def test_load_finds_file_without_extension():
    """Test that prefer.load() can find files without specifying extension."""
    import json
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        test_json_path = os.path.join(temp_dir, "example.json")

        with open(test_json_path, "w") as f:
            json.dump({"found": True, "format": "json"}, f)

        configurator = await prefer.load(
            "example",
            options={
                "loaders": {
                    "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                }
            },
        )

        assert configurator.context == {"found": True, "format": "json"}


@pytest.mark.asyncio
async def test_load_prefers_json_over_other_formats():
    """Test that JSON format is preferred when multiple formats exist."""
    import json
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        json_path = os.path.join(temp_dir, "config.json")
        xml_path = os.path.join(temp_dir, "config.xml")
        ini_path = os.path.join(temp_dir, "config.ini")

        with open(json_path, "w") as f:
            json.dump({"format": "json", "preferred": True}, f)

        with open(xml_path, "w") as f:
            f.write("<config><format>xml</format></config>")

        with open(ini_path, "w") as f:
            f.write("[config]\nformat = ini")

        configurator = await prefer.load(
            "config",
            options={
                "loaders": {
                    "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                }
            },
        )

        assert configurator.context["format"] == "json"
        assert configurator.context["preferred"]


@pytest.mark.asyncio
async def test_load_fails_when_no_matching_file():
    """Test that prefer.load() fails when no file matches."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            await prefer.load(
                "nonexistent",
                options={
                    "loaders": {
                        "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                    }
                },
            )
            assert False, "Should have raised an error for no matching file"

        except ValueError as e:
            assert "No file found matching 'nonexistent'" in str(e)


@pytest.mark.asyncio
async def test_load_with_different_extensions():
    """Test loading files with different extensions."""
    import json
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        files_to_create = {
            "data.json": {"type": "json", "content": "test"},
            "data.yaml": "type: yaml\ncontent: test",
            "data.ini": "[data]\ntype = ini\ncontent = test",
            "data.xml": "<data><type>xml</type><content>test</content></data>",
        }

        for filename, content in files_to_create.items():
            filepath = os.path.join(temp_dir, filename)

            with open(filepath, "w") as f:
                if isinstance(content, dict):
                    json.dump(content, f)
                else:
                    f.write(content)

        for ext in ["json", "yaml", "ini", "xml"]:
            configurator = await prefer.load(
                f"data.{ext}",
                options={
                    "loaders": {
                        "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                    }
                },
            )

            assert configurator.context is not None
            assert (
                "type" in str(configurator.context)
                or "type" in configurator.context
            )


@pytest.mark.asyncio
async def test_load_with_nested_paths():
    """Test loading files from nested directory structures."""
    import json
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        nested_dir = os.path.join(temp_dir, "subdir", "config")
        os.makedirs(nested_dir, exist_ok=True)

        config_path = os.path.join(nested_dir, "app.json")

        with open(config_path, "w") as f:
            json.dump({"nested": True, "path": "deep"}, f)

        configurator = await prefer.load(
            "subdir/config/app",
            options={
                "loaders": {
                    "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                }
            },
        )

        assert configurator.context["nested"]
        assert configurator.context["path"] == "deep"


@pytest.mark.asyncio
async def test_load_fails_with_supported_extension_but_missing_file():
    """Test error message when file with supported extension doesn't exist."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            await prefer.load(
                "nonexistent.json",
                options={
                    "loaders": {
                        "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                    }
                },
            )
            assert False, "Should have raised an error"

        except ValueError as e:
            assert "No file found matching 'nonexistent.json'" in str(e)
            assert "extensions" not in str(e)


@pytest.mark.asyncio
async def test_load_fails_when_no_formatter_matches():
    """Test error when file exists but no formatter matches."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        unknown_file = os.path.join(temp_dir, "config.unknown")

        with open(unknown_file, "w") as f:
            f.write("some content")

        try:
            await prefer.load(
                "config.unknown",
                options={
                    "loaders": {
                        "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                    }
                },
            )
            assert False, "Should have raised an error"

        except ValueError as e:
            assert "No formatter found for:" in str(e)
