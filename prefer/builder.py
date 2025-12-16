"""ConfigBuilder for layered configuration from multiple sources."""

from __future__ import annotations

import abc
import os
import typing

from prefer import configuration as configuration_module
from prefer import loading

if typing.TYPE_CHECKING:
    from collections.abc import Mapping


def deep_merge(
    base: dict[str, typing.Any],
    override: dict[str, typing.Any],
) -> dict[str, typing.Any]:
    """Deep merge two dictionaries, with override taking precedence.

    Args:
        base: The base dictionary to merge into.
        override: The dictionary whose values take precedence.

    Returns:
        A new dictionary with merged values.
    """
    result = base.copy()

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


class Source(abc.ABC):
    """Abstract base class for configuration sources."""

    @abc.abstractmethod
    async def load(
        self,
        options: loading.LoadOptions | None = None,
    ) -> dict[str, typing.Any]:
        """Load configuration from this source.

        Args:
            options: Optional loading options.

        Returns:
            A dictionary of configuration values.
        """
        ...  # pragma: no cover


class MemorySource(Source):
    """Configuration source from an in-memory dictionary."""

    def __init__(self, data: Mapping[str, typing.Any]) -> None:
        self._data = dict(data)

    async def load(
        self,
        options: loading.LoadOptions | None = None,
    ) -> dict[str, typing.Any]:
        return self._data.copy()


class FileSource(Source):
    """Configuration source from a file."""

    def __init__(self, identifier: str) -> None:
        self._identifier = identifier

    async def load(
        self,
        options: loading.LoadOptions | None = None,
    ) -> dict[str, typing.Any]:
        config = await loading.load(self._identifier, options=options)
        return config.context


class OptionalFileSource(Source):
    """Configuration source from a file that may not exist."""

    def __init__(self, identifier: str) -> None:
        self._identifier = identifier

    async def load(
        self,
        options: loading.LoadOptions | None = None,
    ) -> dict[str, typing.Any]:
        try:
            config = await loading.load(self._identifier, options=options)
            return config.context
        except (FileNotFoundError, ValueError):
            return {}


class EnvSource(Source):
    """Configuration source from environment variables.

    Environment variables are mapped to configuration keys by:
    1. Stripping the prefix (if provided)
    2. Converting to lowercase
    3. Replacing double underscores with dots for nesting

    Example:
        With prefix="MYAPP":
        - MYAPP_DATABASE_HOST -> database.host
        - MYAPP_LOG__LEVEL -> log.level (double underscore for explicit dot)
    """

    def __init__(
        self,
        prefix: str | None = None,
        *,
        separator: str = "_",
        nesting_separator: str = "__",
    ) -> None:
        self._prefix = prefix.upper() + separator if prefix else ""
        self._separator = separator
        self._nesting_separator = nesting_separator

    def _parse_key(self, env_key: str) -> list[str]:
        """Parse an environment variable key into config path parts."""
        # Remove prefix
        key = env_key[len(self._prefix) :]

        # Replace nesting separator with a placeholder
        key = key.replace(self._nesting_separator, "\x00")

        # Split by separator and convert to lowercase
        parts = [p.lower() for p in key.split(self._separator)]

        # Restore dots from placeholder
        return [p.replace("\x00", ".") for p in parts]

    def _set_nested(
        self,
        data: dict[str, typing.Any],
        parts: list[str],
        value: str,
    ) -> None:
        """Set a nested value in a dictionary."""
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    async def load(
        self,
        options: loading.LoadOptions | None = None,
    ) -> dict[str, typing.Any]:
        result: dict[str, typing.Any] = {}

        for key, value in os.environ.items():
            if self._prefix and not key.startswith(self._prefix):
                continue

            if not self._prefix:
                # Without prefix, skip common system variables
                continue

            parts = self._parse_key(key)
            if parts:
                self._set_nested(result, parts, value)

        return result


class ConfigBuilder:
    """Builder for layered configuration from multiple sources.

    Sources are applied in order, with later sources overriding earlier ones.
    Deep merge is used for nested dictionaries.

    Example:
        config = await (ConfigBuilder()
            .add_defaults({"database": {"host": "localhost", "port": 5432}})
            .add_file("config/default.toml")
            .add_optional_file("config/local.toml")
            .add_env("MYAPP")
            .build())

        print(config.get("database.host"))
    """

    def __init__(self) -> None:
        self._sources: list[Source] = []
        self._options: loading.LoadOptions | None = None

    def with_options(self, options: loading.LoadOptions) -> ConfigBuilder:
        """Set loading options for file sources.

        Args:
            options: Loading options to use.

        Returns:
            Self for chaining.
        """
        self._options = options
        return self

    def add_source(self, source: Source) -> ConfigBuilder:
        """Add a custom source to the builder.

        Args:
            source: The source to add.

        Returns:
            Self for chaining.
        """
        self._sources.append(source)
        return self

    def add_defaults(
        self,
        defaults: Mapping[str, typing.Any],
    ) -> ConfigBuilder:
        """Add default values.

        Args:
            defaults: Default configuration values.

        Returns:
            Self for chaining.
        """
        self._sources.append(MemorySource(defaults))
        return self

    def add_file(self, identifier: str) -> ConfigBuilder:
        """Add a required configuration file.

        Args:
            identifier: The file identifier to load.

        Returns:
            Self for chaining.

        Raises:
            ValueError: If the file is not found during build.
        """
        self._sources.append(FileSource(identifier))
        return self

    def add_optional_file(self, identifier: str) -> ConfigBuilder:
        """Add an optional configuration file.

        If the file doesn't exist, it's silently skipped.

        Args:
            identifier: The file identifier to load.

        Returns:
            Self for chaining.
        """
        self._sources.append(OptionalFileSource(identifier))
        return self

    def add_env(
        self,
        prefix: str,
        *,
        separator: str = "_",
        nesting_separator: str = "__",
    ) -> ConfigBuilder:
        """Add environment variables as a configuration source.

        Args:
            prefix: The environment variable prefix (e.g., "MYAPP").
            separator: Separator between key parts (default "_").
            nesting_separator: Separator for explicit nesting (default "__").

        Returns:
            Self for chaining.
        """
        self._sources.append(
            EnvSource(prefix, separator=separator, nesting_separator=nesting_separator)
        )
        return self

    async def build(self) -> configuration_module.Configuration:
        """Build the final merged configuration.

        Returns:
            A Configuration object with all sources merged.

        Raises:
            ValueError: If a required file source is not found.
        """
        merged: dict[str, typing.Any] = {}

        for source in self._sources:
            data = await source.load(self._options)
            merged = deep_merge(merged, data)

        return configuration_module.Configuration(context=merged)
