# poor man's quick lambda
# don't want to do the bytecode tricks lol

from fpy.composable.function import func

from typing import TypeVar, Any, Generic, Callable

T = TypeVar("T")
R = TypeVar("R")


class IntermediateFunc(func[R], Generic[R]):
    def __init__(self, fn: Callable[[Any], R]):
        super().__init__(fn)

    def __eq__(self, a: Any) -> Callable[[Any], bool]:
        return lambda x: self(x) == a

    def __ne__(self, a: Any) -> Callable[[Any], bool]:
        return lambda x: self(x) != a

    def __add__(self, n: Any) -> Callable[[Any], Any]:
        return lambda x: self(x) + n

    def __sub__(self, n: Any) -> Callable[[Any], Any]:
        return lambda x: self(x) - n

    def __mul__(self, n: Any) -> Callable[[Any], Any]:
        return lambda x: self(x) * n

    def __div__(self, n: Any) -> Callable[[Any], Any]:
        return lambda x: self(x) / n

    def __radd__(self, n: Any) -> Callable[[Any], Any]:
        return lambda x: n + self(x)

    def __rsub__(self, n: Any) -> Callable[[Any], Any]:
        return lambda x: n - self(x)

    def __rmul__(self, n: Any) -> Callable[[Any], Any]:
        return lambda x: n * self(x)

    def __rdiv__(self, n: Any) -> Callable[[Any], Any]:
        return lambda x: n / self(x)

    def __getattr__(self, *args, **kwargs):
        return func(lambda x: self(x).__getattribute__(*args, **kwargs))

    def __getitem__(self, *args, **kwargs):
        return func(lambda x: self(x).__getitem__(*args, **kwargs))

    def __or__(self, other):
        return lambda x: self(x).__or__(other)

    def __hash__(self):
        return hash(id(self))


class Placeholder:
    def __eq__(self, a: Any) -> Callable[[Any], bool]:
        def __f(x: Any) -> bool:
            return x == a

        return IntermediateFunc(__f)

    def __ne__(self, a: Any) -> Callable[[Any], bool]:
        def __f(x: Any) -> bool:
            return x != a

        return IntermediateFunc(__f)

    def __add__(self, n):
        return IntermediateFunc(lambda x: x + n)

    def __sub__(self, n):
        return IntermediateFunc(lambda x: x - n)

    def __mul__(self, n):
        return IntermediateFunc(lambda x: x * n)

    def __div__(self, n):
        return IntermediateFunc(lambda x: x / n)

    def __radd__(self, n):
        return IntermediateFunc(lambda x: n + x)

    def __rsub__(self, n):
        return IntermediateFunc(lambda x: n - x)

    def __rmul__(self, n):
        return IntermediateFunc(lambda x: n * x)

    def __rdiv__(self, n):
        return IntermediateFunc(lambda x: n / x)

    def __getattr__(self, *args, **kwargs):
        return IntermediateFunc(lambda x: x.__getattribute__(*args, **kwargs))

    def __getitem__(self, *args, **kwargs):
        return IntermediateFunc(lambda x: x.__getitem__(*args, **kwargs))

    def __hash__(self):
        return hash(id(self))

    def __or__(self, other):
        return IntermediateFunc(lambda x: x.__or__(other))


__ = Placeholder()
