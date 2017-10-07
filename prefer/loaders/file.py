import asyncio
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


async def read(path, chunk_size=1024):
    if not os.path.exists(path):
        return

    # TODO: Don't use open/read, as I'm 99% sure they block.
    reader = open(path, 'r')
    result = ''

    while True:
        data = reader.read(chunk_size)

        if not data:
            break

        result += data

    return result


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
        coroutines = [read(path) for path in paths]

        for index in range(len(coroutines)):
            content = await coroutines[index]

            if content:
                return LoadResult(
                    source=paths[index],
                    content=content,
                )
