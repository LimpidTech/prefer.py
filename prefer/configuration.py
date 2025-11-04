from __future__ import annotations

import collections
import typing

from prefer import events

NODE_SEPARATOR = "."


def split_key_from_identifier(identifier: str) -> tuple[str, str]:
    try:
        index = identifier.rindex(".")
        key = identifier[index + 1 :]
        identifier = identifier[:index]

    except ValueError:
        key = identifier
        identifier = ""

    return identifier, key


def split_by_separator(identifier: str) -> typing.Iterator[str]:
    current = ""

    for character in identifier:
        if current and character == NODE_SEPARATOR:
            yield current
            current = ""
            continue

        current += character

    if current:
        yield current


def get_matching_node(
    root: typing.Dict[str, typing.Any],
    identifier: str,
    assign: typing.Optional[typing.Callable[[], typing.Any]] = None,
) -> typing.Any:
    node: typing.Any = root

    for key in split_by_separator(identifier):
        print(node, key)
        if assign and key not in node:
            node[key] = assign()

        if key not in node:
            raise ValueError(f"{identifier} is an unset identifier")

        node = node[key]

    return node


class Configuration(events.Emitter):
    context: typing.Dict[str, typing.Any]
    formatter: typing.Optional[typing.Any]
    loader: typing.Optional[typing.Any]

    @classmethod
    def using(
        cls,
        data: typing.Optional[
            typing.Union["Configuration", typing.Dict[str, typing.Any]]
        ],
    ) -> "Configuration":
        if data is None:
            return cls()

        if isinstance(data, cls):
            return data

        if isinstance(data, dict):
            return cls(context=data)

        return cls()

    def __init__(
        self,
        *,
        context: typing.Optional[typing.Dict[str, typing.Any]] = None,
        formatter: typing.Optional[typing.Any] = None,
        loader: typing.Optional[typing.Any] = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__()

        if context is None:
            context = {}

        self.context = context
        self.formatter = formatter
        self.loader = loader

    def get(self, identifier: str) -> typing.Any:
        try:
            return get_matching_node(self.context, identifier)
        except ValueError:
            return None

    def set(self, identifier: str, value: typing.Any) -> typing.Any:
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

        self.emit("changed", identifier, value, previous_value)
        return node.get(key)

    def save(self) -> None:
        raise NotImplementedError("save is not yet implemented")

    def __getitem__(self, key: str) -> typing.Any:
        return self.context[key]

    def __setitem__(self, key: str, value: typing.Any) -> None:
        previous_value = self.context.get(key)
        self.context[key] = value
        self.emit("changed", key, value, previous_value)

    def __delitem__(self, key: str) -> None:
        del self.context[key]

    def __eq__(self, subject: object) -> bool:
        if subject is self:
            return True

        return subject == self.context

    def __contains__(self, subject: str) -> bool:
        return subject in self.context
