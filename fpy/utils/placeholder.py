# poor man's quick lambda
# don't want to do the bytecode tricks lol

from fpy.composable.function import func


class Placeholder:
    def __eq__(self, a):
        return lambda x: x == a

    def __ne__(self, a):
        return lambda x: x != a

    def __or__(self, fn):
        return func(fn)

    def __add__(self, n):
        return lambda x: x + n

    def __sub__(self, n):
        return lambda x: x - n

    def __mul__(self, n):
        return lambda x: x * n

    def __div__(self, n):
        return lambda x: x / n

    def __radd__(self, n):
        return lambda x: n + x

    def __rsub__(self, n):
        return lambda x: n - x

    def __rmul__(self, n):
        return lambda x: n * x

    def __rdiv__(self, n):
        return lambda x: n / x

    def __getattr__(self, *args, **kwargs):
        return func(lambda x: x.__getattribute__(*args, **kwargs))

    def __getitem__(self, *args, **kwargs):
        return func(lambda x: x.__getitem__(*args, **kwargs))

    def __hash__(self):
        return hash(id(self))

    def __or__(self, other):
        return lambda x: x.__or__(other)


__ = Placeholder()
