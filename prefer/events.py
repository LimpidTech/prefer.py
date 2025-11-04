from __future__ import annotations

import collections
import typing


class Emitter:
    def __init__(self) -> None:
        self.event_handlers: collections.defaultdict[
            str, list[typing.Callable[..., typing.Any]]
        ] = collections.defaultdict(list)

    def emit(
        self, event_name: str, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        handlers = self.event_handlers[event_name]

        if len(handlers) == 0:
            del self.event_handlers[event_name]

        for handler in handlers:
            handler(event_name, *args, **kwargs)

    def bind(
        self, event_name: str, handler: typing.Callable[..., typing.Any]
    ) -> None:
        self.event_handlers[event_name].append(handler)
