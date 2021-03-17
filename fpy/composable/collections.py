from fpy.composable.function import func, NotEnoughArgsError
from fpy.data.forgetful import Under
from fpy.data.function import const

import collections.abc as cabc


def get_item(c, *args, **kwargs):
    return c.__getitem__(*args, **kwargs)


class Seq(func):
    def __init__(self, l):
        assert isinstance(l, cabc.Sequence), f"{l} is not a sequence"
        self._l = l
        super().__init__(get_item, l)

    def __getattr__(self, *args, **kwargs):
        return self._l.__getattribute__(*args, **kwargs)


class Map(func):
    def __init__(self, m):
        assert isinstance(m, cabc.Mapping), f"{m} is not a map"
        self._m = m
        super().__init__(get_item, m)

    def __getattr__(self, *args, **kwargs):
        return self._m.__getattribute__(*args, **kwargs)


@func
def transN(n, fn, it):
    return type(it)((fn(v) if _i == n else v for _i, v in enumerate(it)))


trans0 = transN(0)
trans1 = transN(1)


@func
def setN(n, v, it):
    return transN(n, const(v), it)


set0 = setN(0)
set1 = setN(1)


@func
def getN(n, x):
    return x[n]


get0 = getN(0)
get1 = getN(1)


def of_(*it):
    return func(lambda x: x in it)


def is_(ty):
    return func(lambda x: isinstance(x, ty))


def and_(a, b):
    @func
    def __and(*args, **kwargs):
        _a = a(*args, **kwargs)
        if _a:
            return b(*args, **kwargs)
        return _a

    return __and


def or_(a, b):
    @func
    def __or(*args, **kwargs):
        _a = a(*args, **kwargs)
        if not _a:
            return b(*args, **kwargs)
        return _a

    return __or


@func
def to(dst, src):
    return dst(src)


def apply(fn):
    @func
    def __apply(_a=None, _k=None):
        a = _a if _a is not None else ()
        k = _k if _k is not None else {}
        return fn(*a, **k)

    return __apply


@func
def mapN(n, fn, *lsts):
    if len(lsts) < n:
        raise NotEnoughArgsError(n, len(lsts))
    ap = apply(fn)
    return [ap(row) for row in zip(*lsts)]


mp1 = mapN(1)
mp2 = mapN(2)


@func
def eqN(n, it, x):
    return x == it[n]


eq0 = eqN(0)
eq1 = eqN(1)

fwd_ = Under.ret
