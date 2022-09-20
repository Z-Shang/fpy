from __future__ import annotations

from abc import ABCMeta, abstractmethod, abstractclassmethod
from fpy.control.functor import _Functor

from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

T = TypeVar("T")
S = TypeVar("S")


class _Applicative(_Functor[T], Generic[T]):
    @classmethod
    def pure(cls, val):
        return cls(val)

    @classmethod
    def liftA2(cls, f, a, b):
        return cls.fmap(cls.fmap(f, a), b)


@dataclass
class Applicative(_Applicative[T], Generic[T]):
    val: T

    def __fmap__(self, f: Callable[[T], S]) -> _Applicative[S]:
        return type(self)(f(self.val))
