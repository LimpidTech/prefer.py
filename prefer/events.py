import collections


class Emitter:
    def __init__(self):
        self.event_handlers = collections.defaultdict(list)

    def emit(self, event_name, *args, **kwargs):
        handlers = self.event_handlers[event_name]

        if len(handlers) is 0:
            del self.event_handlers[event_name]

        for handler in handlers:
            handler(event_name, *args, **kwargs)

    def bind(self, event_name, handler):
        self.event_handlers[event_name].append(handler)
