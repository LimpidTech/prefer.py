import copy
import decimal
import functools
import operator
import typing

from prefer import events


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

        if context is None:
            context = {}

        self.context = context
        self.formatter = formatter
        self.loader = loader

    def save(self):
        raise NotImplementedError('save is not yet implemented')

    def __getitem__(self, key):
        return self.context[key]

    def __setitem__(self, key, value):
        self.context[key] = value

    def __delitem__(self, key):
        del self.context[key]

    def __eq__(self, subject):
        if subject is self:
            return True

        return subject == self.context

    def __contains__(self, subject):
        return subject in self.context
