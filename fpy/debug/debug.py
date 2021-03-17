import sys

from fpy.composable.function import func


@func
def trace(txt, val):
    print(txt, val, file=sys.stderr)
    return val


def showio(fn):
    def res(*args, **kwargs):
        print(f"{fn.__name__} input: {args, kwargs}", file=sys.stderr)
        ret = fn(*args, **kwargs)
        print(f"{fn.__name__} output: {ret}", file=sys.stderr)
        return ret

    return res
