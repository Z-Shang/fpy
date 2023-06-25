def _fresh(*n, _rec={}):
    v = _rec.get(n, 0) + 1
    _rec[n] = v
    return "_{}_{}".format("_".join(n), v)


class _v:
    def __init__(self, n=None):
        self.n = n or _fresh("_v")

    def __hash__(self):
        return hash(self.n)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "#v<{}>".format(self.n)

    def __call__(self, *args, **kw):
        raise TypeError(f"_v Object is not callable, {self} called with: {args}, {kw}")


class NonExhaustivePatternError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class pytternd:
    """
    usage:
    pytternd(
        {
            (1, 2, 3): True
            (_v(1), _v(2), 4): False
            ...
        }
    )[1, 2, 4] = False

    referencing variable in body is not supported until this is made into a decorator
    """

    def __init__(self, d: dict):
        self.orig_d = d
        # print(f"{d = }")
        self.varp = dict()
        patlen = [len(k) for k in d.keys()]
        assert len(set(patlen)) == 1, "Currently patterns must of same length"
        self._len = patlen[0]
        self._prepare(d)

    def _prepare(self, d: dict):
        ks = list(d.keys())
        if not ks:
            return d
        assert not self._check_overlap_q(ks), "Cannot have overlapping patterns"
        if len(ks[0]) == 1:
            varp = {}
            res = {}
            for k, v in d.items():
                if isinstance(k[0], _v):
                    varp[()] = v
                    continue
                res[k[0]] = v
            self.varp = varp
            self.d = res
            return
        new = {}
        varp = {}
        for k, v in d.items():
            if isinstance(k[0], _v):
                varp[k[1:]] = v
                continue
            new[k[0]] = {k[1:]: v, **new.get(k[0], {})}
        if varp:
            self.varp = pytternd(varp)
        self.d = {k: pytternd(v) for k, v in new.items()} if len(ks[0]) > 1 else new

    def _check_overlap_q(self, ks):
        if len(ks[0]) > 1:
            return False
        return all([isinstance(k, _v) for k in ks])

    def __getitem__(self, vs):
        x, *xs = vs
        assert len(vs) == self._len, "Number of value doesn't match pattern length"

        if xs:
            try:
                return self.d[x].__getitem__(xs)
            except Exception as e:
                if self.varp:
                    return self.varp.__getitem__(xs)
                raise NonExhaustivePatternError(
                    "There is no pattern matching value: {}".format(vs)
                ) from None
        try:
            return self.d[x]
        except:
            try:
                return self.varp[()]
            except:
                raise NonExhaustivePatternError(
                    "There is no pattern matching value: {}".format(vs)
                ) from None

    def match(self, *vs, default=None):
        try:
            return self.__getitem__(vs)
        except NonExhaustivePatternError:
            return default

    def __len__(self):
        return self._len

    def __repr__(self):
        return str({**self.d, **({"<v>": self.varp} if self.varp else {})})


if __name__ == "__main__":
    test = pytternd(
        {(1, 2, 3): True, (_v(1), _v(2), 4): False, (_v(1), _v(2), _v(3)): "Huh?"}
    )
    print(test[1, 2, 3])
    print(test[1, 2, 4])
    print(test[1, 2, 5])
