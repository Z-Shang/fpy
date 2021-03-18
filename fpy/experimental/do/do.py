import bytecode as bc

import pprint

from fpy.parsec.parsec import parser, ptrans, one, many
from fpy.composable.collections import (
    of_,
    is_,
    and_,
    or_,
    trans0,
    fwd_,
    get0,
    mp1,
    apply,
)
from fpy.data.function import id_, const
from fpy.data.forgetful import forget
from fpy.data.maybe import Just, isJust, fromJust
from fpy.data.either import Left, Right, rights, either
from fpy.utils.placeholder import __
from fpy.composable.function import func
from fpy.debug.debug import trace

from dataclasses import dataclass

import dis

pp = pprint.PrettyPrinter(indent=4)


@dataclass
class Arrow:
    lineno: int


@dataclass
class TupleArrow:
    lineno: int
    ntpl: int


@dataclass
class Ret:
    lineno: int


isInstr = is_(bc.Instr)
isArrow = is_(Arrow)
dash = and_(isInstr, __.name == "UNARY_NEGATIVE")
arrowHead = and_(isInstr, and_(__.name == "COMPARE_OP", __.arg == bc.Compare.LT))
popTop = and_(isInstr, __.name == "POP_TOP")
none = and_(isInstr, and_(__.name == "LOAD_CONST", __.arg == None))
mkTpl = and_(isInstr, __.name == "BUILD_TUPLE")
ret = and_(isInstr, __.name == "RETURN_VALUE")
load = and_(
    isInstr,
    __.name
    ^ of_(
        "LOAD_GLOBAL",
        "LOAD_NAME",
        "LOAD_FAST",
        "LOAD_CLOSURE",
        "LOAD_DEREF",
        "LOAD_CLASSDEREF",
    ),
)
store = and_(
    isInstr,
    __.name
    ^ of_(
        "STORE_FAST",
        "STORE_NAME",
        "STORE_DEREF",
    ),
)
parseArrow = ptrans(
    one(dash) << one(arrowHead) << one(popTop),
    trans0(trans0(__.lineno ^ Arrow)),
)
parseTplArrow = ptrans(
    one(dash) >> one(arrowHead) >> one(mkTpl) << one(popTop),
    trans0(trans0(lambda x: TupleArrow(x.lineno, x.arg))),
)
parseNoneRet = many(
    ptrans(
        one(popTop) << one(none) << one(ret),
        trans0(trans0(__.lineno ^ Ret)),
    )
    | one(const(True))
)

parseDo = many(parseTplArrow | parseArrow | one(const(True)))
isFast = and_(isInstr, __.name == "LOAD_FAST")
fastToCell = ptrans(
    one(isFast),
    trans0(trans0(__.arg ^ bc.CellVar ^ func(bc.Instr, "LOAD_DEREF"))),
)
isSFast = and_(isInstr, __.name == "STORE_FAST")
storeFastToCell = ptrans(
    one(isSFast),
    trans0(trans0(__.arg ^ bc.CellVar ^ func(bc.Instr, "STORE_DEREF"))),
)
transFast = many(fastToCell | storeFastToCell | one(const(True)))


@dataclass
class ArrowInst:
    comp: list
    argnames: list
    nxt: list


def transformRet(insts):
    res = []
    for inst in insts:
        if isinstance(inst, Ret):
            res.append(bc.Instr("RETURN_VALUE", lineno=inst.lineno))
            continue
        if ret(inst):
            res.append(bc.Instr("LOAD_DEREF", bc.CellVar("!ret"), lineno=inst.lineno))
            res.append(bc.Instr("ROT_TWO", lineno=inst.lineno))
            res.append(bc.Instr("CALL_FUNCTION", 1, lineno=inst.lineno))
            # res.append(bc.Instr("DUP_TOP", lineno=inst.lineno))
            # res.append(bc.Instr("PRINT_EXPR", lineno=inst.lineno))
            res.append(bc.Instr("RETURN_VALUE", lineno=inst.lineno))
            continue
        res.append(inst)
    return res


def partitionInst(insts, n):
    if not insts:
        return [], []
    if n == 0:
        return [], insts
    head = insts[-1]
    # print(f"{head = }")
    # print(f"{n = }")
    pre, post = head.pre_and_post_stack_effect()
    # print(f"{pre = }")
    # print(f"{post= }")
    if pre >= 0:
        if pre == n:
            return [head], insts[:-1]
        if pre < n:
            nxt, rst = partitionInst(insts[:-1], n - pre)
            return nxt + [head], rst
    pre = abs(pre)
    nxt, rst = partitionInst(insts[:-1], pre)
    if post == n:
        return nxt + [head], rst
    if post < n:
        head = nxt + [head]
        nxt, rst = partitionInst(rst, n - post)
        return nxt + head, rst


def transformDo(insts):
    # pp.pprint(insts)
    res = []
    while insts:
        inst = insts.pop()
        if not isinstance(inst, (Arrow, TupleArrow)):
            res.insert(0, inst)
            continue
        if isinstance(inst, Arrow):
            comp, insts = partitionInst(insts, 1)
            bindName = insts.pop()
            assert load(bindName) or (
                isInstr(bindName) and bindName.name == "BUILD_TUPLE"
            ), "it has to be tuple of symbols on the left of <-"
            if load(bindName):
                name = bindName.arg
                res = [ArrowInst(comp, [name], res)]
                continue
            if isInstr(bindName) and bindName.name == "BUILD_TUPLE":
                narg = bindName.arg
                names = []
                for _ in range(narg):
                    name = insts.pop()
                    assert load(name), "it has to be tuple of symbols on the left of <-"
                    names.insert(0, name.arg)
                res = [ArrowInst(comp, names, res)]
                continue
        elif isinstance(inst, TupleArrow):
            comp, insts = partitionInst(insts, 1)
            names = []
            for _ in range(inst.ntpl):
                name = insts.pop()
                assert load(name), "it has to be tuple of symbols on the left of <-"
                names.insert(0, name.arg)
            res = [ArrowInst(comp, names, res)]
            continue

    return res


def generateLocal(insts, argnames, fv, cv, name, filename):
    resBc = []
    bcobj = bc.Bytecode(resBc)
    bcobj.freevars = fv
    bcobj.cellvars = cv
    bcobj.name = name
    bcobj.filename = filename
    bcobj.docstring = "generated local function for binding in do notation"
    bcobj.argcount = 1
    bcobj.argname.extend(argnames)
    co = bcobj.to_code()
    return co


def build_do_func(name, arg, body, free):
    inner = doDeco(body, name, arg, free)
    return inner


markArg = lambda args: (lambda x: Right(x) if load(x) and x.arg in args else Left(x))
toArg = __.arg ^ bc.CellVar ^ func(bc.Instr, "LOAD_DEREF")
isCell = and_(
    isInstr,
    and_(
        __.name ^ of_("LOAD_DEREF", "STORE_DEREF", "LOAD_CLOSURE"),
        __.arg ^ is_(bc.CellVar),
    ),
)
transFree = lambda free: (
    lambda x: bc.Instr("LOAD_DEREF", bc.FreeVar(x.arg))
    if and_(isInstr, and_(__.name == "LOAD_GLOBAL", __.arg ^ of_(*free)))(x)
    else x
)
markFree = lambda free: (
    lambda x: Right(x) if isCell(x) and x.arg.name in free else Left(x)
)
toFree = lambda x: bc.Instr(x.name, bc.FreeVar(x.arg.name))


@func
def doArrow(name, cells, free, arrow):
    if not isinstance(arrow, ArrowInst):
        return [arrow]
    bind_fn_name = f"{name}.__do_bind_{'_'.join(arrow.argnames)}__"
    arrfn = build_do_func(bind_fn_name, arrow.argnames, arrow.nxt, [*cells, *free])
    # print(f"{bind_fn_name = }")
    rawcomp = arrow.comp
    # print(f"{rawcomp = }")
    transcomp = (
        mp1(markArg([arrow.argnames, *free, *cells]))
        ^ mp1(either(id_, toArg))
        ^ mp1(markFree(free))
        ^ mp1(either(id_, toFree))
        ^ transFree(free)
    )(rawcomp)
    # print(f"{transcomp = }")
    res = [
        *transcomp,
        # bc.Instr("DUP_TOP", lineno=arrow.comp[-1].lineno),
        # bc.Instr("PRINT_EXPR", lineno=arrow.comp[-1].lineno),
        bc.Instr("LOAD_ATTR", "__bind__", lineno=arrow.comp[-1].lineno),
    ]
    ncells = len(cells)
    for cell in cells:
        res.append(bc.Instr("LOAD_CLOSURE", bc.CellVar(cell)))
    for f in free:
        if f not in cells:
            res.append(bc.Instr("LOAD_CLOSURE", bc.FreeVar(f)))
            ncells += 1
    if cells:
        res.append(bc.Instr("BUILD_TUPLE", ncells))
    res.append(bc.Instr("LOAD_CONST", arrfn))
    res.append(
        bc.Instr(
            "LOAD_CONST",
            bind_fn_name,
            lineno=arrow.comp[-1].lineno,
        )
    )
    res.append(bc.Instr("MAKE_FUNCTION", 0x08, lineno=arrow.comp[-1].lineno))
    if len(arrow.argnames) > 1:
        res.append(bc.Instr("LOAD_CONST", apply))
        res.append(bc.Instr("ROT_TWO"))
        res.append(bc.Instr("CALL_FUNCTION", 1))
    res.append(bc.Instr("CALL_FUNCTION", 1, lineno=arrow.comp[-1].lineno))
    res.append(bc.Instr("RETURN_VALUE", lineno=arrow.comp[-1].lineno))
    return res


def doDeco(b, name, args, free):
    # print(f"{free = }")
    # print("RAW BC: ", b)
    res = (
        parseDo(b) >> (get0 ^ transFast) & forget
        | get0
        ^ mp1(markFree(free))
        ^ mp1(either(id_, toFree))
        ^ mp1(markArg(args))
        ^ mp1(either(id_, toArg))
        ^ mp1(transFree(free))
        ^ transformDo
    )
    # print("Trans BC: ", res.under())
    getCellName = lambda x: Right(x) if isCell(x) else Left(x)
    cells = res | mp1(getCellName) | rights | mp1(__.arg.name) | __ + list(args) | set
    # print(f"{cells = }")
    res = (
        res
        | mp1(doArrow(name, cells.under(), free))
        | func(sum, start=[]) ^ bc.Bytecode
    )
    resbc = res.under()
    # pp.pprint(resbc)
    resbc.cellvars.extend(cells.under())
    resbc.cellvars.extend(free)
    resbc.freevars.extend(free)
    resbc.argcount = len(args)
    resbc.argnames.extend(args)
    resbc.name = name
    resbc.filename = name
    resbc.flags = resbc.flags | 16
    resbc.update_flags()
    co = resbc.to_code()
    # print("======================")
    # print(name)
    # print("======================")
    # dis.dis(co)
    # dis.show_code(co)
    return co


def do(m):
    def res(fn):
        ret = m
        # add `!ret` to the front of function
        retbc = [
            bc.Instr("LOAD_CONST", m),
            bc.Instr("LOAD_ATTR", "ret"),
            bc.Instr("STORE_DEREF", bc.CellVar("!ret")),
        ]
        rawbc = bc.Bytecode.from_code(fn.__code__)
        args = fn.__code__.co_varnames[: fn.__code__.co_argcount]
        b = parseNoneRet(retbc + rawbc) & forget | get0 | transformRet
        co = doDeco(b.under(), fn.__name__, args, rawbc.freevars)
        fn.__code__ = co
        return fn

    return res
