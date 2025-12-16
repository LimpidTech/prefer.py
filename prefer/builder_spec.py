import json
import os
import tempfile
from unittest import mock

import pytest

from prefer.builder import (
    ConfigBuilder,
    EnvSource,
    FileSource,
    MemorySource,
    OptionalFileSource,
    Source,
    deep_merge,
)


class TestDeepMerge:
    """Tests for the deep_merge function."""

    def test_simple_merge(self) -> None:
        """Test merging flat dictionaries."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        result = deep_merge(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self) -> None:
        """Test merging nested dictionaries."""
        base = {"database": {"host": "localhost", "port": 5432}}
        override = {"database": {"port": 3306, "name": "test"}}

        result = deep_merge(base, override)

        assert result == {
            "database": {"host": "localhost", "port": 3306, "name": "test"}
        }

    def test_override_replaces_non_dict(self) -> None:
        """Test that non-dict values are replaced entirely."""
        base = {"key": "string_value"}
        override = {"key": {"nested": "value"}}

        result = deep_merge(base, override)

        assert result == {"key": {"nested": "value"}}

    def test_base_dict_replaced_by_scalar(self) -> None:
        """Test that a dict can be replaced by a scalar."""
        base = {"key": {"nested": "value"}}
        override = {"key": "scalar"}

        result = deep_merge(base, override)

        assert result == {"key": "scalar"}

    def test_does_not_modify_original(self) -> None:
        """Test that the original dictionaries are not modified."""
        base = {"a": 1}
        override = {"b": 2}

        deep_merge(base, override)

        assert base == {"a": 1}
        assert override == {"b": 2}


class TestMemorySource:
    """Tests for the MemorySource class."""

    @pytest.mark.asyncio
    async def test_load_returns_data_copy(self) -> None:
        """Test that load returns a copy of the data."""
        data = {"key": "value"}
        source = MemorySource(data)

        result = await source.load()

        assert result == {"key": "value"}
        assert result is not data

    @pytest.mark.asyncio
    async def test_load_with_options(self) -> None:
        """Test that load works with options parameter."""
        source = MemorySource({"key": "value"})

        result = await source.load(options={"loaders": None})

        assert result == {"key": "value"}


class TestFileSource:
    """Tests for the FileSource class."""

    @pytest.mark.asyncio
    async def test_load_existing_file(self) -> None:
        """Test loading an existing configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")

            with open(config_path, "w") as f:
                json.dump({"key": "value"}, f)

            source = FileSource("config")
            result = await source.load(
                options={
                    "loaders": {
                        "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                    }
                }
            )

            assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_load_nonexistent_file_raises(self) -> None:
        """Test that loading a nonexistent file raises an error."""
        source = FileSource("/nonexistent/path/config.json")

        with pytest.raises(ValueError):
            await source.load()


class TestOptionalFileSource:
    """Tests for the OptionalFileSource class."""

    @pytest.mark.asyncio
    async def test_load_existing_file(self) -> None:
        """Test loading an existing configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")

            with open(config_path, "w") as f:
                json.dump({"key": "value"}, f)

            source = OptionalFileSource("config")
            result = await source.load(
                options={
                    "loaders": {
                        "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                    }
                }
            )

            assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_load_nonexistent_file_returns_empty(self) -> None:
        """Test that loading a nonexistent file returns empty dict."""
        source = OptionalFileSource("/nonexistent/path/config.json")

        result = await source.load()

        assert result == {}


class TestEnvSource:
    """Tests for the EnvSource class."""

    @pytest.mark.asyncio
    async def test_load_with_prefix(self) -> None:
        """Test loading environment variables with a prefix."""
        with mock.patch.dict(
            os.environ,
            {
                "MYAPP_DATABASE_HOST": "localhost",
                "MYAPP_DATABASE_PORT": "5432",
                "OTHER_VAR": "ignored",
            },
            clear=True,
        ):
            source = EnvSource("MYAPP")
            result = await source.load()

            assert result == {
                "database": {
                    "host": "localhost",
                    "port": "5432",
                }
            }

    @pytest.mark.asyncio
    async def test_load_with_nesting_separator(self) -> None:
        """Test loading environment variables with explicit nesting."""
        with mock.patch.dict(
            os.environ,
            {"MYAPP_LOG__LEVEL": "debug"},
            clear=True,
        ):
            source = EnvSource("MYAPP")
            result = await source.load()

            assert result == {"log.level": "debug"}

    @pytest.mark.asyncio
    async def test_load_without_prefix_returns_empty(self) -> None:
        """Test that loading without prefix returns empty dict."""
        with mock.patch.dict(
            os.environ,
            {"SOME_VAR": "value"},
            clear=True,
        ):
            source = EnvSource(None)
            result = await source.load()

            assert result == {}

    @pytest.mark.asyncio
    async def test_case_insensitive_prefix(self) -> None:
        """Test that prefix matching is case-insensitive."""
        with mock.patch.dict(
            os.environ,
            {"MYAPP_KEY": "value"},
            clear=True,
        ):
            source = EnvSource("myapp")
            result = await source.load()

            assert result == {"key": "value"}


class TestConfigBuilder:
    """Tests for the ConfigBuilder class."""

    @pytest.mark.asyncio
    async def test_build_empty(self) -> None:
        """Test building with no sources."""
        builder = ConfigBuilder()
        config = await builder.build()

        assert config.context == {}

    @pytest.mark.asyncio
    async def test_add_defaults(self) -> None:
        """Test adding default values."""
        config = await ConfigBuilder().add_defaults({"key": "value"}).build()

        assert config.get("key") == "value"

    @pytest.mark.asyncio
    async def test_add_file(self) -> None:
        """Test adding a file source."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")

            with open(config_path, "w") as f:
                json.dump({"key": "from_file"}, f)

            config = await (
                ConfigBuilder()
                .with_options(
                    {
                        "loaders": {
                            "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                        }
                    }
                )
                .add_file("config")
                .build()
            )

            assert config.get("key") == "from_file"

    @pytest.mark.asyncio
    async def test_add_optional_file_exists(self) -> None:
        """Test adding an optional file that exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")

            with open(config_path, "w") as f:
                json.dump({"key": "from_file"}, f)

            config = await (
                ConfigBuilder()
                .with_options(
                    {
                        "loaders": {
                            "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                        }
                    }
                )
                .add_optional_file("config")
                .build()
            )

            assert config.get("key") == "from_file"

    @pytest.mark.asyncio
    async def test_add_optional_file_missing(self) -> None:
        """Test adding an optional file that doesn't exist."""
        config = await (
            ConfigBuilder()
            .add_defaults({"key": "default"})
            .add_optional_file("/nonexistent/config.json")
            .build()
        )

        assert config.get("key") == "default"

    @pytest.mark.asyncio
    async def test_add_env(self) -> None:
        """Test adding environment variable source."""
        with mock.patch.dict(os.environ, {"MYAPP_KEY": "from_env"}, clear=True):
            config = await ConfigBuilder().add_env("MYAPP").build()

            assert config.get("key") == "from_env"

    @pytest.mark.asyncio
    async def test_layered_override(self) -> None:
        """Test that later sources override earlier ones."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")

            with open(config_path, "w") as f:
                json.dump({"key": "from_file", "other": "file_value"}, f)

            with mock.patch.dict(os.environ, {"MYAPP_KEY": "from_env"}, clear=True):
                config = await (
                    ConfigBuilder()
                    .with_options(
                        {
                            "loaders": {
                                "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                            }
                        }
                    )
                    .add_defaults({"key": "default", "default_only": "yes"})
                    .add_file("config")
                    .add_env("MYAPP")
                    .build()
                )

                # Environment overrides file, file overrides defaults
                assert config.get("key") == "from_env"
                assert config.get("other") == "file_value"
                assert config.get("default_only") == "yes"

    @pytest.mark.asyncio
    async def test_deep_nested_override(self) -> None:
        """Test deep merge behavior with nested values."""
        with mock.patch.dict(
            os.environ,
            {"MYAPP_DATABASE_PASSWORD": "secret"},
            clear=True,
        ):
            config = await (
                ConfigBuilder()
                .add_defaults(
                    {
                        "database": {
                            "host": "localhost",
                            "port": 5432,
                            "name": "mydb",
                        }
                    }
                )
                .add_env("MYAPP")
                .build()
            )

            # Environment adds password without overwriting other values
            assert config.get("database.host") == "localhost"
            assert config.get("database.port") == 5432
            assert config.get("database.password") == "secret"

    @pytest.mark.asyncio
    async def test_with_options(self) -> None:
        """Test setting loading options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")

            with open(config_path, "w") as f:
                json.dump({"key": "value"}, f)

            config = await (
                ConfigBuilder()
                .with_options(
                    {
                        "loaders": {
                            "prefer.loaders.file:FileLoader": {"paths": [temp_dir]}
                        }
                    }
                )
                .add_file("config")
                .build()
            )

            assert config.get("key") == "value"

    @pytest.mark.asyncio
    async def test_add_source_custom(self) -> None:
        """Test adding a custom source."""

        class CustomSource(Source):
            async def load(
                self,
                options: dict | None = None,
            ) -> dict:
                return {"custom": "value"}

        config = await ConfigBuilder().add_source(CustomSource()).build()

        assert config.get("custom") == "value"

    @pytest.mark.asyncio
    async def test_required_file_missing_raises(self) -> None:
        """Test that missing required file raises an error."""
        builder = ConfigBuilder().add_file("/nonexistent/config.json")

        with pytest.raises(ValueError):
            await builder.build()

    @pytest.mark.asyncio
    async def test_add_env_with_custom_separators(self) -> None:
        """Test environment source with custom separators."""
        with mock.patch.dict(
            os.environ,
            {"MYAPP-DATABASE-HOST": "localhost"},
            clear=True,
        ):
            config = await (
                ConfigBuilder().add_env("MYAPP", separator="-").build()
            )

            assert config.get("database.host") == "localhost"

    @pytest.mark.asyncio
    async def test_fluent_api_chaining(self) -> None:
        """Test that all methods return self for chaining."""
        builder = ConfigBuilder()

        result = (
            builder.with_options({})
            .add_defaults({})
            .add_optional_file("/nonexistent")
        )

        assert result is builder
