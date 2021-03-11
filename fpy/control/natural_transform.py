from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable


F = TypeVar("F")
G = TypeVar("G")
A = TypeVar("A")
B = TypeVar("B")


class _NTrans(Generic[F, A, G, B], metaclass=ABCMeta):
    @abstractmethod
    def __trans__(self, v: A) -> G[B]:
        raise NotImplementedError

    def __call__(self, v: A) -> G[B]:
        return self.__trans__(v)


@dataclass
class NTrans(_NTrans):
    f: Callable[[A], G[B]]

    def __trans__(self, v: F[A]) -> G[B]:
        assert hasattr(v, "__ntrans__")
        return v.__ntrans__(self.f)
