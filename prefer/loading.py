import typing
import importlib

from prefer import configuration
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
    plugin_list: typing.List[str],
    defaults: typing.List[str],
) -> typing.List[object]:

    if plugin_list is None:
        plugin_list = defaults

    for Kind in map(import_plugin, plugin_list):
        if Kind.provides(identifier):
            return Kind


async def load(
    identifier: str, *,
    config: typing.Dict[str, typing.Any]={},
) -> configuration.Configuration:

    Formatter = find_matching_plugin(
        identifier=identifier,
        defaults=formatters.defaults,
        plugin_list=config.get('formatters'),
    )

    Loader = find_matching_plugin(
        identifier=identifier,
        defaults=loaders.defaults,
        plugin_list=config.get('loaders'),
    )

    formatter = Formatter()
    loader = Loader()

    loader_result = await loader.load(identifier)
    context = await formatter.deserialize(loader_result.content)

    return configuration.Configuration(
        context=context,
        identifier=identifier,
        source=loader_result.source,
        loader=loader,
        formatter=formatter,
    )
