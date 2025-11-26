from __future__ import annotations

import collections
import importlib
import os
import typing
import urllib.parse

from prefer.formatters import defaults as formatters
from prefer.loaders import loader

LoadResult = collections.namedtuple(
    "LoadResult",
    [
        "source",
        "content",
    ],
)


def import_plugin(identifier: str) -> typing.Any:
    module_name, object_type = identifier.split(":")
    module = importlib.import_module(module_name)
    plugin_class = getattr(module, object_type)

    return plugin_class


def read(path: str, chunk_size: int = 1024) -> typing.Optional[str]:
    if not os.path.exists(path):
        return None

    with open(path) as reader:
        result = ""

        while True:
            data = reader.read(chunk_size)

            if not data:
                break

            result += data

        return result


class FileLoader(loader.Loader):
    @staticmethod
    def provides(identifier: str) -> bool:
        parsed = urllib.parse.urlparse(identifier)
        return not parsed.scheme or parsed.scheme == "file"

    async def locate(self, identifier: str) -> list[str]:
        """Search paths for a file matching the provided identifier."""

        # TODO: Async this!

        exact_match = self._get_exact_match(identifier)
        if exact_match:
            return [exact_match]

        candidates = []
        for path in self.paths:
            candidates.extend(self._get_candidates_for_path(path, identifier))
        return candidates

    def _get_exact_match(self, identifier: str) -> typing.Optional[str]:
        for path in self.paths:
            if not os.path.exists(path):
                continue
            identifier_path = os.path.join(path, identifier)
            if self._is_secure_path(identifier_path, path) and os.path.exists(
                identifier_path
            ):
                return identifier_path
        return None

    def _is_secure_path(self, full_path: str, base_path: str) -> bool:
        return os.path.abspath(full_path).startswith(
            os.path.abspath(base_path)
        )

    def _get_candidates_for_path(
        self, path: str, identifier: str
    ) -> list[str]:
        if not os.path.exists(path):
            return []

        if self._has_extension(identifier):
            checker = self._make_basename_secure_checker(
                path, os.path.basename(identifier)
            )
            paths_iter = map(
                lambda name: os.path.join(path, name), os.listdir(path)
            )
            return list(filter(checker, paths_iter))
        else:
            checker = self._make_secure_exists_checker(path)
            exts = self._get_supported_extensions()
            paths_iter = map(
                lambda ext: os.path.join(path, identifier + ext), exts
            )
            return list(filter(checker, paths_iter))

    def _has_extension(self, identifier: str) -> bool:
        """Check if identifier already has a file extension."""
        return "." in os.path.basename(identifier)

    def _get_supported_extensions(self) -> list[str]:
        formatter_identifiers = (
            self.configuration.get("formatters") or formatters.defaults
        )

        extensions = []
        for identifier in formatter_identifiers:
            formatter = import_plugin(identifier)
            for ext in formatter.extensions():
                if ext not in extensions:
                    extensions.append(ext)
        return extensions

    @staticmethod
    def _make_basename_secure_checker(
        base_path: str, target_basename: str
    ) -> typing.Callable[[str], bool]:
        def check(p: str) -> bool:
            return os.path.basename(p) == target_basename and os.path.abspath(
                p
            ).startswith(os.path.abspath(base_path))

        return check

    @staticmethod
    def _make_secure_exists_checker(
        base_path: str,
    ) -> typing.Callable[[str], bool]:
        def check(p: str) -> bool:
            return os.path.abspath(p).startswith(
                os.path.abspath(base_path)
            ) and os.path.exists(p)

        return check

    async def load(self, identifier: str) -> typing.Optional[LoadResult]:
        """Load content from a configuration."""

        paths = await self.locate(identifier)

        for path in paths:
            content = read(path)

            if content:
                return LoadResult(
                    source=path,
                    content=content,
                )

        return None
