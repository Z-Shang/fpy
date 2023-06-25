from __future__ import annotations

from fpy.control.monad import _Monad
from fpy.composable.function import func, SignatureMismatchError
from fpy.composable.collections import get0, get1
from fpy.data.function import id_, const

import bytecode as bc

from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, Tuple

import sys

T = TypeVar("T")
R = TypeVar("R")
S = TypeVar("S")

@dataclass
class State(_Monad[S], Generic[S, T]):
    comp : Callable[[S], Tuple[T, S]]

    @classmethod
    def ret(cls, v : T):
        def res(s : S) -> Tuple[T, S]:
            return v, s
        return cls(res)

    def __bind__(self, b : Callable[[T], State[S, R]]) -> State[S, R]:
        def res(s: S):
            _v, _s = runState(self, s)
            return runState(b(_v), _s)
        return State(res)

def runState(c : State[S, T], s : S) -> Tuple[T, S]:
    return c.comp(s)

def get() -> State[S, S]:
    return State(lambda s: (s, s))

def put(x: S) -> State[None, S]:
    return State(const((None, x)))

def modify(f : Callable[[S], S]) -> State[S, None]:
    return get() >> (lambda x: put(f(x)))

def gets(f : Callable[[S], T]) -> State[S, T]:
    return get() >> (lambda x: State.ret(f(x)))

def evalState(comp : State[S, T], s : S) -> T:
    return get0(runState(comp, s))

def execState(comp : State[S, T], s : S) -> T:
    return get1(runState(comp, s))
