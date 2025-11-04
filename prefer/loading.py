from __future__ import annotations

import collections.abc
import importlib
import typing

from prefer import configuration as configuration_module
from prefer.formatters import defaults as formatters
from prefer.loaders import defaults as loaders

UNSET = "unset"


def import_plugin(identifier: str) -> typing.Any:
    module_name, object_type = identifier.split(":")
    module = importlib.import_module(module_name)
    plugin_class = getattr(module, object_type)
    return plugin_class


def find_matching_plugin(
    identifier: str,
    plugin_list: typing.Optional[
        typing.Union[list[str], dict[str, dict[str, typing.Any]]]
    ],
    defaults: list[str],
) -> tuple[
    typing.Optional[typing.Any],
    typing.Optional[configuration_module.Configuration],
]:
    Plugin: typing.Optional[typing.Any] = None
    configuration: typing.Optional[configuration_module.Configuration] = None

    if plugin_list is None:
        plugin_list = defaults

    for plugin_identifier in plugin_list:
        Kind = import_plugin(plugin_identifier)

        if Kind.provides(identifier):
            Plugin = Kind

            if not isinstance(plugin_list, collections.abc.Sequence):
                configuration = configuration_module.Configuration.using(
                    plugin_list[plugin_identifier],
                )

            break

    return Plugin, configuration


async def load(
    identifier: str,
    *,
    configuration: typing.Optional[dict[str, typing.Any]] = None,
) -> configuration_module.Configuration:
    if configuration is None:
        configuration = {}

    Formatter, formatter_configuration = find_matching_plugin(
        identifier=identifier,
        defaults=formatters.defaults,
        plugin_list=configuration.get("formatters"),
    )

    Loader, loader_configuration = find_matching_plugin(
        identifier=identifier,
        defaults=loaders.defaults,
        plugin_list=configuration.get("loaders"),
    )

    if Formatter is None or Loader is None:
        raise ValueError(
            f"No formatter or loader found for identifier: {identifier}"
        )

    formatter = Formatter(configuration=formatter_configuration)
    loader = Loader(configuration=loader_configuration)

    loader_result = await loader.load(identifier)
    context = await formatter.deserialize(loader_result.content)

    return configuration_module.Configuration(
        context=context,
        loader=loader,
        formatter=formatter,
    )
