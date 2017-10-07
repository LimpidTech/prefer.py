import typing

from prefer import configuration as configuration_module
from prefer import events
from prefer import pathing


LoaderConfigurationType = typing.Union[
    typing.Dict[str, typing.Any],
    configuration_module.Configuration,
]


class Loader(events.Emitter):
    def __init__(
        self, *,
        configuration: LoaderConfigurationType=None,
    ):
        self.configuration = configuration_module.Configuration.using(configuration)

        paths: typing.List[str] = self.configuration.get('paths')

        if paths is None:
            paths = pathing.get_system_paths()

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
