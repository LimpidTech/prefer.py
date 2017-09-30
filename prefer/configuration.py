import decimal
import functools
import operator
import typing


class Configuration(object):
    def __init__(self, *,
        context: typing.Optional[typing.Any]=None, 
        formatter: typing.Optional['prefer.formatter.Formatter']=None,
        loader: typing.Optional['prefer.loader.Loader']=None,
        **kwargs: typing.Optional[typing.Dict[str, typing.Any]],
    ):

        if context is None:
            context = {}

        self.context = context

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
