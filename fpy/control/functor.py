from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

from fpy.control.natural_transform import _NTrans
from fpy.composable.function import func

T = TypeVar("T")
F = TypeVar("F")
G = TypeVar("G")
A = TypeVar("A")
B = TypeVar("B")


class _Functor(Generic[T], metaclass=ABCMeta):
    @classmethod
    def fmap(cls, f: Callable[[A], B], a: _Functor[A]) -> _Functor[B]:
        assert isinstance(a, cls)
        return a.__fmap__(f)

    def __fmap__(self, f: Callable[[T], B]) -> _Functor[B]:
        raise NotImplementedError

    def __ntrans__(self, t: _NTrans[_Functor, T, G, B]) -> G[B]:
        """
        Natrual transformation:
        __ntrans__ :: f a -> (f a -> g b) -> g b
        """
        raise NotImplementedError

    def __and__(self, t: _NTrans[_Functor, T, G, B]) -> G[B]:
        return t.__trans__(self)

    def __or__(self, f):
        return self.__fmap__(f)


@dataclass
class Functor(_Functor[T], Generic[T]):
    val: T

    def __fmap__(self, f: Callable[[T], B]) -> _Functor[B]:
        return type(self)(f(self.val))

    def __ntrans__(self, t: Callable[[T], G[B]]) -> G[B]:
        return t(self.val)


@func
def fmap(o: F[A], f: Callable[[A], B]) -> F[B]:
    return o.__fmap__(f)
