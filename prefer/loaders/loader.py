from __future__ import annotations

import typing

from prefer import configuration as configuration_module
from prefer import events, pathing

LoaderConfigurationType = typing.Union[
    typing.Dict[str, typing.Any],
    configuration_module.Configuration,
]


class Loader(events.Emitter):
    configuration: configuration_module.Configuration
    paths: list[str]

    def __init__(
        self,
        *,
        configuration: typing.Optional[LoaderConfigurationType] = None,
    ) -> None:
        self.configuration = configuration_module.Configuration.using(
            configuration
        )

        paths: typing.Optional[list[str]] = self.configuration.get("paths")

        if paths is None:
            paths = pathing.get_system_paths()

        self.paths = paths

    @staticmethod
    def provides(identifier: str) -> bool:
        raise NotImplementedError(
            'Loader objects must implement a static "provides" method.',
        )

    async def locate(self, identifier: str) -> typing.Any:
        return identifier

    async def load(self, identifier: str) -> typing.Any:
        raise NotImplementedError(
            'Loader objects must implement a "load" method.',
        )
