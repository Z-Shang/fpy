from fpy.composable.function import func

from typing import TypeVar, Callable

T = TypeVar("T")
F = TypeVar("F")
A = TypeVar("A")
B = TypeVar("B")


def id_(x: T) -> T:
    return x


@func
def const(x: T, _: any) -> T:
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
