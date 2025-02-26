from fpy.composable.function import func

from typing import TypeVar, Callable, Any

T = TypeVar("T")
F = TypeVar("F")
A = TypeVar("A")
B = TypeVar("B")


def id_(x: T) -> T:
    return x


@func
def const(x: T, _: Any) -> T:
    return x


@func
def flip(f: Callable[[B, A], T], a: A, b: B) -> T:
    return f(b, a)


def fix(f: Callable) -> Callable:
    fn = func(f)
    return lambda *args: fn(fix(fn))(*args)


@func
def on(b: Callable[[B, B], T], u: Callable[[A], B], x: A, y: A) -> T:
    return b(u(x), u(y))

@func
def constN(n: int, x):
    if n == 1:
        return const(x)
    return const(constN(n - 1, x))

def uncurryN(n: int, f):
    def _res(*args):
        if len(args) != n:
            raise TypeError(f"Uncurried function {f} expected {n} arguments but {len(args)} was given")
        part = f
        for i in range(n):
            part = part(args[i])
        return part

    return _res
