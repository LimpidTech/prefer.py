import collections
import os
import typing
import urllib

from prefer import configuration
from prefer.loaders import loader

LoadResult = collections.namedtuple('LoadResult', [
    'source',
    'content',
])


class FileLoader(loader.Loader):
    @staticmethod
    def provides(identifier: str):
        parsed = urllib.parse.urlparse(identifier)
        return not parsed.scheme or parsed.scheme == 'file'

    async def locate(self, identifier: str):
        """ Search paths for a file matching the provided identifier. """

        # TODO: Async this!

        file_paths = []

        for path in self.paths:
            if not os.path.exists(path):
                continue

            identifier_path = os.path.join(path, identifier)

            if os.path.exists(identifier_path):
                # Exact match always wins
                file_paths = [identifier_path]
                break

            for name in os.listdir(path):
                match_path = os.path.join(path, name)
                if match_path.startswith(identifier_path):
                    file_paths.append(match_path)

        return file_paths

    async def load(self, identifier: str):
        """ Load content from a configuration. """

        paths = await self.locate(identifier)

        if not paths:
            return None

        path = paths[0]

        with open(path, 'r') as source:
            content = source.read()

        return LoadResult(source=path, content=content)
