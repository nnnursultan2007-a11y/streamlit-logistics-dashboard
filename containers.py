"""
ЛАБОРАТОРНАЯ №4 — ЗАДАНИЕ 1
Функциональные контейнеры Maybe / Either.

Maybe  = Just(value) | Nothing()   — значение может отсутствовать.
Either = Right(value) | Left(error) — успех или ошибка (ошибка — данные, не исключение).

Все контейнеры неизменяемы (frozen dataclass), методы возвращают новые объекты.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
F = TypeVar("F")


# =========================
# MAYBE
# =========================

class Maybe(Generic[T]):
    """Базовый класс. Используйте Just / Nothing."""

    def is_just(self) -> bool:
        raise NotImplementedError

    def is_nothing(self) -> bool:
        return not self.is_just()

    def map(self, fn: Callable[[T], U]) -> "Maybe[U]":
        raise NotImplementedError

    def bind(self, fn: Callable[[T], "Maybe[U]"]) -> "Maybe[U]":
        raise NotImplementedError

    def filter(self, predicate: Callable[[T], bool]) -> "Maybe[T]":
        raise NotImplementedError

    def get_or_else(self, default: Any) -> Any:
        raise NotImplementedError

    def to_either(self, error: E) -> "Either[E, T]":
        raise NotImplementedError


@dataclass(frozen=True)
class Just(Maybe[T]):
    value: T

    def is_just(self) -> bool:
        return True

    def map(self, fn):
        return Just(fn(self.value))

    def bind(self, fn):
        return fn(self.value)

    def filter(self, predicate):
        return self if predicate(self.value) else Nothing()

    def get_or_else(self, default):
        return self.value

    def to_either(self, error):
        return Right(self.value)


@dataclass(frozen=True)
class Nothing(Maybe[Any]):
    def is_just(self) -> bool:
        return False

    def map(self, fn):
        return self

    def bind(self, fn):
        return self

    def filter(self, predicate):
        return self

    def get_or_else(self, default):
        return default

    def to_either(self, error):
        return Left(error)


# =========================
# EITHER
# =========================

class Either(Generic[E, T]):
    """Базовый класс. Используйте Left / Right."""

    def is_right(self) -> bool:
        raise NotImplementedError

    def is_left(self) -> bool:
        return not self.is_right()

    def map(self, fn: Callable[[T], U]) -> "Either[E, U]":
        raise NotImplementedError

    def map_left(self, fn: Callable[[E], F]) -> "Either[F, T]":
        raise NotImplementedError

    def bind(self, fn: Callable[[T], "Either[E, U]"]) -> "Either[E, U]":
        raise NotImplementedError

    def get_or_else(self, default: Any) -> Any:
        raise NotImplementedError

    def fold(self, on_left: Callable[[E], U], on_right: Callable[[T], U]) -> U:
        raise NotImplementedError

    def to_maybe(self) -> Maybe[T]:
        raise NotImplementedError


@dataclass(frozen=True)
class Right(Either[Any, T]):
    value: T

    def is_right(self) -> bool:
        return True

    def map(self, fn):
        return Right(fn(self.value))

    def map_left(self, fn):
        return self

    def bind(self, fn):
        return fn(self.value)

    def get_or_else(self, default):
        return self.value

    def fold(self, on_left, on_right):
        return on_right(self.value)

    def to_maybe(self):
        return Just(self.value)


@dataclass(frozen=True)
class Left(Either[E, Any]):
    error: E

    def is_right(self) -> bool:
        return False

    def map(self, fn):
        return self

    def map_left(self, fn):
        return Left(fn(self.error))

    def bind(self, fn):
        return self

    def get_or_else(self, default):
        return default

    def fold(self, on_left, on_right):
        return on_left(self.error)

    def to_maybe(self):
        return Nothing()
