"""Generic registry for mapping service types to their factories."""

from typing import Generic, TypeVar

KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")


class Registry(Generic[KeyT, ValueT]):
    """A typed mapping from an enum key to a registered value.

    Values are typically zero-argument factory callables that build a
    concrete service instance on demand.
    """

    def __init__(self) -> None:
        self._items: dict[KeyT, ValueT] = {}

    def register(self, key: KeyT, value: ValueT) -> None:
        """Register a value under ``key``, rejecting duplicate keys."""
        if key in self._items:
            raise ValueError(f"Service already registered: {key!r}")
        self._items[key] = value

    def get(self, key: KeyT) -> ValueT:
        """Return the value registered under ``key``."""
        try:
            return self._items[key]
        except KeyError:
            raise KeyError(f"Unknown service: {key!r}") from None
