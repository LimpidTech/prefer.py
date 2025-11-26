from __future__ import annotations

import collections.abc
import importlib
import typing

from prefer import configuration as configuration_module
from prefer.formatters import defaults as formatters
from prefer.loaders import defaults as loaders

UNSET = "unset"


class LoadOptions(typing.TypedDict, total=False):
    formatters: typing.Optional[
        typing.Union[list[str], dict[str, dict[str, typing.Any]]]
    ]

    loaders: typing.Optional[
        typing.Union[list[str], dict[str, dict[str, typing.Any]]]
    ]


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
    options: typing.Optional[LoadOptions] = None,
) -> configuration_module.Configuration:
    if options is None:
        options = {}

    Loader, loader_options = find_matching_plugin(
        identifier=identifier,
        defaults=loaders.defaults,
        plugin_list=options.get("loaders"),
    )

    if Loader is None:
        raise ValueError(f"No loader found for identifier: {identifier}")

    if loader_options is None:
        loader_options = configuration_module.Configuration()

    loader_options.set(
        "formatters", options.get("formatters") or formatters.defaults
    )
    loader = Loader(configuration=loader_options)
    loader_result = await loader.load(identifier)

    if loader_result is None:
        Formatter, _ = find_matching_plugin(
            identifier=identifier,
            defaults=formatters.defaults,
            plugin_list=options.get("formatters"),
        )

        if Formatter is not None:
            raise ValueError(f"No file found matching '{identifier}'")

        formatter_list = options.get("formatters") or formatters.defaults
        format_names = [
            f.split(":")[1].replace("Formatter", "") for f in formatter_list
        ]

        raise ValueError(
            f"No file found matching '{identifier}' with "
            f"{', '.join(format_names)} extensions"
        )

    actual_identifier = loader_result.source

    Formatter, formatter_options = find_matching_plugin(
        identifier=actual_identifier,
        defaults=formatters.defaults,
        plugin_list=options.get("formatters"),
    )

    if Formatter is None:
        raise ValueError(f"No formatter found for: {actual_identifier}")

    formatter = Formatter(configuration=formatter_options)
    context = await formatter.deserialize(loader_result.content)

    return configuration_module.Configuration(
        context=context,
        loader=loader,
        formatter=formatter,
    )
