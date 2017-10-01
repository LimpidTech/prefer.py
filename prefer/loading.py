import collections
import importlib
import typing

from prefer import configuration as configuration_module
from prefer.formatters import defaults as formatters
from prefer.loaders import defaults as loaders

UNSET = 'unset'


def import_plugin(identifier: str):
    module_name, object_type = identifier.split(':')
    module = importlib.import_module(module_name)
    object_type = getattr(module, object_type)
    return object_type


def find_matching_plugin(
    identifier: str,
    plugin_list: typing.Union[typing.List[str], typing.Dict[str, typing.Dict[str, typing.Any]]],
    defaults: typing.List[str],
) -> typing.List[object]:

    Plugin = None
    configuration = None

    if plugin_list is None:
        plugin_list = defaults

    for plugin_identifier in plugin_list:
        Kind = import_plugin(plugin_identifier)

        if Kind.provides(identifier):
            Plugin = Kind

            if not isinstance(plugin_list, collections.Sequence):
                configuration = configuration_module.Configuration.using(
                    plugin_list[plugin_identifier],
                )

            break

    return Plugin, configuration


async def load(
    identifier: str, *,
    configuration: typing.Dict[str, typing.Any]={},
) -> configuration_module.Configuration:

    Formatter, formatter_configuration = find_matching_plugin(
        identifier=identifier,
        defaults=formatters.defaults,
        plugin_list=configuration.get('formatters'),
    )

    Loader, loader_configuration = find_matching_plugin(
        identifier=identifier,
        defaults=loaders.defaults,
        plugin_list=configuration.get('loaders'),
    )

    formatter = Formatter(configuration=formatter_configuration)
    loader = Loader(configuration=loader_configuration)

    loader_result = await loader.load(identifier)
    context = await formatter.deserialize(loader_result.content)

    return configuration_module.Configuration(
        context=context,
        identifier=identifier,
        source=loader_result.source,
        loader=loader,
        formatter=formatter,
    )
