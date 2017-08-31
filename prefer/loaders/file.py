import collections
import os
import urllib

LoaderResult = collections.namedtuple('LoaderResult', [
    'source',
    'content',
])


class FileLoader(object):
    @staticmethod
    def provides(identifier: str):
        parsed = urllib.parse.urlparse(identifier)
        return not parsed.scheme or parsed.scheme == 'file'

    async def load(self, identifier: str):
        source_identifier = os.path.abspath(identifier)

        with open(source_identifier, 'r') as source:
            content = source.read()

        return LoaderResult(
            source=source_identifier,
            content=content,
        )
