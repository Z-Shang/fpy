from __future__ import annotations

from fpy.control.monad import _Monad
from fpy.composable.function import func, SignatureMismatchError

import bytecode as bc

from dataclasses import dataclass
from typing import TypeVar, Generic, Callable


T = TypeVar("T")
R = TypeVar("R")
S = TypeVar("S")


@dataclass
class Cont(_Monad[R], Generic[T, R]):
    f: Callable[[T], R]

    def __init__(self, f):
        self.f = func(f)

    def __bind__(self, f):
        return self.__class__.ret(lambda k: self.f(lambda *a: f(*a).__run__(k)))

    def __ntrans__(self, t):
        return self.f(t)

    def __call__(self, *a, **k):
        try:
            res = self.f(*a, **k)
            if isinstance(res, func) and res.f is self.f:
                return Cont(res)
            return Cont(lambda k: k(res))
        except SignatureMismatchError as e:
            raise e.e

    def __run__(self, k: Cont[[R], S]):
        return self.f(k)


def runCont(c, k):
    return c.__run__(k)


def to_cont(v):
    return Cont(lambda k: k(v))


def cont(f: Callable[[T], R]) -> Cont[T, R]:
    raw_bc = bc.Bytecode.from_code(f.__code__)

    print(raw_bc)
    res_bc = []
    for inst in raw_bc:
        if not isinstance(inst, bc.Instr):
            res_bc.append(inst)
            continue
        if inst.name != "RETURN_VALUE":
            res_bc.append(inst)
            continue

        res_bc.append(bc.Instr("LOAD_CONST", to_cont, lineno=inst.lineno))
        res_bc.append(bc.Instr("ROT_TWO", lineno=inst.lineno))
        res_bc.append(bc.Instr("CALL_FUNCTION", 1, lineno=inst.lineno))
        res_bc.append(inst)
    print(res_bc)
    bc_obj = bc.Bytecode(res_bc)
    bc_obj.freevars = f.__code__.co_freevars
    bc_obj.cellvars = f.__code__.co_cellvars
    bc_obj.argcount = f.__code__.co_argcount
    bc_obj.name = f.__name__
    f.__code__ = bc_obj.to_code()
    return func(f)
