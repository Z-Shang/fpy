import inspect
import collections.abc as cabc

from fpy.composable.composable import Composable
from fpy.composable.transparent import Transparent

from typing import Callable


class SignatureMismatchError(Exception):
    def __init__(self, e):
        self.e = e


class NotEnoughArgsError(Exception):
    def __init__(self, expect, got):
        self.expect = expect
        self.got = got


class func(Composable, Transparent):
    fn: Callable = None

    def __init__(self, f, *args, **kwargs):
        if isinstance(f, func):
            self.fn = f.fn
            self.args = (*f.args, *args)
            self.kwargs = {**f.kwargs, **kwargs}
            self.sig = f.sig
        elif isinstance(f, cabc.Callable):
            self.fn = f
            self.args = args
            self.kwargs = kwargs
            self.sig = inspect.signature(f)
        else:
            raise TypeError(f"{f} is not callable")

    def __underlying__(self):
        return self.fn

    def __repr__(self):
        return repr(self.fn)

    def __call__(self, *args, **kwargs):
        _args = (*self.args, *args)
        _kwargs = {**self.kwargs, **kwargs}
        try:
            self.sig.bind(*_args, **_kwargs)
            return self.fn(*_args, **_kwargs)
        except TypeError:
            try:
                self.sig.bind_partial(*_args, **_kwargs)
                return func(self, *args, **kwargs)
            except TypeError as e:
                raise SignatureMismatchError(e)
        except NotEnoughArgsError:
            return func(self, *args, **kwargs)

    def __compose__(self, other):
        if isinstance(other, func):
            return func(lambda *args, **kwargs: other(self(*args, **kwargs)))
        if isinstance(other, cabc.Callable):
            fn = func(other)
            return func(lambda *args, **kwargs: fn(self(*args, **kwargs)))
        raise TypeError(f"Cannot compose function with {type(other)}")
