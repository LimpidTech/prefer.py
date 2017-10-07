import collections
import copy
import decimal
import functools
import operator
import typing

from prefer import events


NODE_SEPARATOR = '.'


def split_key_from_identifier(identifier):
    try:
        index = identifier.rindex('.')
        key = identifier[index+1:]
        identifier = identifier[:index]

    except ValueError:
        key = identifier
        identifier = ''

    return identifier, key



def split_by_separator(identifier):
    current = ''

    for character in identifier:
        if current and character == NODE_SEPARATOR:
            yield current
            current = ''
            continue

        current += character

    if current:
        yield current

    raise StopIteration()


def get_matching_node(
    root: str,
    identifier: str,
    assign: typing.Callable[[], typing.Any]=None
):

    node = root
    current_identifier = ''

    for key in split_by_separator(identifier):
        print(node, key)
        if assign and key not in node:
            node[key] = assign()

        if key not in node:
            raise ValueError('{} is an unset identifier'.format(
                identifier,
            ))

        node = node[key]

    return node


class Configuration(events.Emitter):
    @classmethod
    def using(Kind, data):
        if data is None:
            return Kind()

        if isinstance(data, Kind):
            return data
            
        return Kind(context=data)

    def __init__(self, *,
        context: typing.Optional[typing.Any]=None, 
        formatter: typing.Optional['prefer.formatter.Formatter']=None,
        loader: typing.Optional['prefer.loader.Loader']=None,
        **kwargs: typing.Optional[typing.Dict[str, typing.Any]],
    ):

        super().__init__()

        if context is None:
            context = {}

        self.context = context
        self.formatter = formatter
        self.loader = loader

    def get(self, identifier):
        try:
            return get_matching_node(self.context, identifier)
        except ValueError:
            return None

    def set(self, identifier, value):
        identifier, key = split_key_from_identifier(identifier)

        if identifier:
            node = get_matching_node(
                self.context,
                identifier,
                assign=collections.OrderedDict,
            )

        else:
            node = self.context

        previous_value = node.get(key)
        node[key] = value

        self.emit('changed', identifier, value, previous_value)
        return node.get(key)

    def save(self):
        raise NotImplementedError('save is not yet implemented')

    def __getitem__(self, key):
        return self.context[key]

    def __setitem__(self, key, value):
        previous_value = self.context.get(key)
        self.context[key] = value
        self.emit('changed', key, value, previous_value)

    def __delitem__(self, key):
        del self.context[key]

    def __eq__(self, subject):
        if subject is self:
            return True

        return subject == self.context

    def __contains__(self, subject):
        return subject in self.context
