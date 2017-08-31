import typing

from prefer import configuration as configuration_module
from prefer import pathing


class Loader(object):
    def __init__(
        self, *,
        paths: typing.Optional[typing.List[str]]=None,
        configuration: configuration_module.Configuration=None,
    ):

        if configuration is None:
            configuration = configuration_module.Configuration()

        if paths is None:
            paths = pathing.get_system_paths()

        self.configuration = configuration
        self.paths = paths

    @staticmethod
    def provides(identifier: str):
        raise NotImplementedError(
            'Loader objects must implement a static "provides" method.',
        )

    async def locate(self, identifier: str):
        return identifier

    async def load(self, identifier: str):
        raise NotImplementedError(
            'Loader objects must implement a "load" method.',
        )
