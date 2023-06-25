import bytecode as bc
import fpy.experimental.pattern.core as pat_core

from fpy.data.function import const
from fpy.composable.collections import is_, and_, or_, get1, mp1, trans0, get0, to
from fpy.composable.function import func
from fpy.data.forgetful import forget
from fpy.data.maybe import Just, Nothing, isJust, fromJust
from fpy.data.either import either, fromRight
from fpy.experimental.do import do
from fpy.parsec.parsec import one, many, neg, skip, many1, ptrans, s2c
from fpy.utils.placeholder import __

from fpy.debug.debug import trace

from dataclasses import dataclass
from typing import List

import sys

import dis

isInstr = is_(bc.Instr)
popTop = and_(isInstr, __.name == "POP_TOP")
none = and_(isInstr, and_(__.name == "LOAD_CONST", __.arg == None))
ret = and_(isInstr, __.name == "RETURN_VALUE")
ending = one(popTop) >> one(none) >> one(ret)
mkConstMap = and_(isInstr, __.name == "BUILD_CONST_KEY_MAP")
mkMap = and_(isInstr, __.name == "BUILD_MAP")
isArg = and_(isInstr, __.name == "LOAD_FAST")
isLoadGlobal = and_(isInstr, __.name == "LOAD_GLOBAL")
isVarName = lambda x: x != "_" and x.startswith("_")
if sys.version_info.major == 3 and sys.version_info.minor >= 11:
    isVar = and_(isLoadGlobal, __.arg ^ get1 ^ isVarName)
    callInst = one(and_(isInstr, __.name == "PRECALL")) >> one(
        and_(isInstr, __.name == "CALL")
    )
    isWildcard = and_(isLoadGlobal, __.arg ^ get1 == "_")
else:
    isWildcard = and_(isLoadGlobal, __.arg == "_")
    isVar = and_(isLoadGlobal, __.arg ^ isVarName)
    callInst = one(and_(isInstr, __.name == "CALL_FUNCTION"))

storeFast = and_(isInstr, __.name == "STORE_FAST")
unpack = and_(isInstr, __.name == "UNPACK_SEQUENCE")

isVarargFn = lambda fn: 1 == ((fn.__code__.co_flags >> 2) & 1)

rightToMaybe = either(const(Nothing()), Just)

@dataclass
class CaseHead:
    args: List[str]


@dataclass
class CaseBody:
    insts: List[bc.Instr]


@dataclass
class StoreName:
    instrs: List[bc.Instr]


@dataclass
class Case:
    head: CaseHead
    body: CaseBody
    store: StoreName


def exprToLambda(b, place, filename, args, fv, v=None):
    varMap = {arg: pat_core._fresh(arg) for arg in args}
    mod_b = []
    free_vars = []
    # print(f"{b = }")
    for instr in b:
        if isArg(instr):
            name = instr.arg
            if name in varMap:
                instr.arg = varMap[name]
            else:
                instr = bc.Instr("LOAD_DEREF", bc.FreeVar(name))
                free_vars.append(name)
        if isVar(instr):
            if sys.version_info.major == 3 and sys.version_info.minor >= 11:
                name = instr.arg[1]
            else:
                name = instr.arg
            assert name in v, f"Variable: {name} is not bound"
            instr = bc.Instr("LOAD_FAST", varMap[v[name]])
        if isLoadGlobal(instr):
            name = instr.arg[1]
            if name in varMap:
                instr = bc.Instr("LOAD_FAST", varMap[name])
        mod_b.append(instr)
    mod_b.append(bc.Instr("RETURN_VALUE"))
    if free_vars and sys.version_info.major == 3 and sys.version_info.minor >= 11:
        mod_b.insert(0, bc.Instr("COPY_FREE_VARS", len(free_vars)))
    # print(f"{mod_b = }")
    lm = bc.Bytecode(mod_b)
    lm.freevars.extend(fv)
    lm.freevars.extend(free_vars)
    lm.argcount = len(varMap)
    lm.argnames.extend(list(varMap.values()))
    lm.name = pat_core._fresh(place, "exprlambda")
    lm.filename = filename
    lm.flags = lm.flags | 16
    lm.update_flags()
    co = lm.to_code()
    # print("=" * 20)
    # dis.dis(co)
    # dis.show_code(co)
    # print("=" * 20)
    return [
        *[bc.Instr("LOAD_CLOSURE", bc.CellVar(f)) for f in free_vars],
        *([bc.Instr("BUILD_TUPLE", len(free_vars))] if free_vars else []),
        bc.Instr("LOAD_CONST", co),
        *([] if sys.version_info.major == 3 and sys.version_info.minor >= 11 else [bc.Instr("LOAD_CONST", lm.name)]),
        bc.Instr("MAKE_FUNCTION", 0x08 if free_vars else 0),
    ], free_vars


def generateDefault(place, filename, args):
    varMap = {arg: pat_core._fresh(arg) for arg in args}
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        lm = bc.Bytecode(
            [
                bc.Instr("PUSH_NULL"),
                bc.Instr("LOAD_CONST", pat_core.NonExhaustivePatternError),
            ]
        )
    else:
        lm = bc.Bytecode([bc.Instr("LOAD_CONST", pat_core.NonExhaustivePatternError)])
    lm.append(bc.Instr("LOAD_CONST", f"Non Exhaustive Pattern Matching: {place}"))
    for k, v in varMap.items():
        lm.append(bc.Instr("LOAD_CONST", f"\n{k}: "))
        lm.append(bc.Instr("LOAD_FAST", v))
        lm.append(bc.Instr("FORMAT_VALUE", 0x02))
    lm.append(bc.Instr("BUILD_STRING", 1 + 2 * len(varMap)))
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        lm.append(bc.Instr("PRECALL", 1))
        lm.append(bc.Instr("CALL", 1))
    else:
        lm.append(bc.Instr("CALL_FUNCTION", 1))
    lm.append(bc.Instr("RAISE_VARARGS", 1))
    lm.argcount = len(varMap)
    lm.argnames.extend(list(varMap.values()))
    lm.name = pat_core._fresh(place, "defaultcase")
    lm.filename = filename
    lm.flags = lm.flags | 16
    lm.update_flags()
    co = lm.to_code()
    return [
        bc.Instr("LOAD_CONST", co),
        *([] if sys.version_info.major == 3 and sys.version_info.minor >= 11 else [bc.Instr("LOAD_CONST", lm.name)]),
        bc.Instr("MAKE_FUNCTION", 0),
    ]


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
    if pre > 0:
        if pre == n:
            return [head], insts[:-1]
        if pre < n:
            nxt, rst = partitionInst(insts[:-1], n - pre)
            return nxt + [head], rst
    if pre == 0:
        nxt, rst = partitionInst(insts[:-1], n - post)
        return nxt + [head], rst
    pre = abs(pre)
    nxt, rst = partitionInst(insts[:-1], pre)
    if post < n:
        head = nxt + [head]
        nxt, rst = partitionInst(rst, n - post)
        return nxt + head, rst
    # if post == n:
    return nxt + [head], rst


def transConstMap(case_inst: Case, fn_name, filename, args, fv):
    body = case_inst.body.insts[:-1]
    mk = case_inst.body.insts[-1]
    keynames = body[-1]
    exprs = []
    rest = body[:-1]
    args = case_inst.head.args
    while rest:
        expr, rest = partitionInst(rest, 1)
        exprs.append(expr)
    lms = [exprToLambda(e, fn_name, filename, args, fv) for e in reversed(exprs)]
    free_vars = set()
    for _, fvs in lms:
        if fvs:
            free_vars.update(fvs)
    resbc = bc.Bytecode(
        sum(
            map(get0, lms),
            start=(
                [bc.Instr("PUSH_NULL")]
                if sys.version_info.major == 3 and sys.version_info.minor >= 11
                else []
            ),
        )
    )
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        for cell in free_vars:
            resbc.insert(0, bc.Instr("MAKE_CELL", bc.CellVar(cell)))
    resbc.append(keynames)
    resbc.append(mk)
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        resbc.append(bc.Instr("LOAD_METHOD", "get"))
        for arg in args:
            resbc.append(bc.Instr("LOAD_FAST", arg))
        if len(args) > 1:
            resbc.append(bc.Instr("BUILD_TUPLE", arg=len(args)))
        resbc.extend(generateDefault(fn_name, filename, args))
        resbc.append(bc.Instr("PRECALL", 2))
        resbc.append(bc.Instr("CALL", 2))
        for arg in args:
            resbc.append(bc.Instr("LOAD_FAST", arg))
        resbc.append(bc.Instr("PRECALL", arg=len(args)))
        resbc.append(bc.Instr("CALL", arg=len(args)))
    else:
        resbc.append(bc.Instr("LOAD_METHOD", "get"))
        for arg in args:
            resbc.append(bc.Instr("LOAD_FAST", arg))
        resbc.append(bc.Instr("BUILD_TUPLE", arg=len(args)))
        resbc.extend(generateDefault(fn_name, filename, args))
        resbc.append(bc.Instr("CALL_METHOD", 2))
        for arg in args:
            resbc.append(bc.Instr("LOAD_FAST", arg))
        resbc.append(bc.Instr("CALL_FUNCTION", arg=len(args)))
    resbc.extend(case_inst.store.instrs)
    return resbc

def transVarMap(case_inst : Case, fn_name, filename, args, fv):
    body = case_inst.body.insts[:-1]
    mk = case_inst.body.insts[-1]
    parts = []
    rest = body
    hasDefault = False
    defaultExpr = []
    args = case_inst.head.args
    free_vars = set()
    while rest:
        part, rest = partitionInst(rest, 2)
        expr, pat = partitionInst(part, 1)
        if isWildcard(pat[0]) and len(pat) == 1:
            assert not hasDefault, f"Duplicated default cases in {fn_name}, line {pat[0].lineno} @ {filename}"
            hasDefault = True
            defaultExpr, fvs = exprToLambda(expr, fn_name, filename, args, fv)
            free_vars.update(fvs)
        else:
            vbind = {}
            vpat = []
            mkTpl = pat[-1]
            raw_pat_parts = pat[:-1] # fromRight([[], []], many(globalName | one(const(True)))(pat[:-1]))[0]
            pat_parts = []
            while raw_pat_parts:
                pat_part, raw_pat_parts = partitionInst(raw_pat_parts, 1)
                pat_parts.append(pat_part)
            for i, v in enumerate(reversed(pat_parts)):
                if len(v) == 1 and isVar(v[0]):
                    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
                        vbind[v[0].arg[1]] = args[i]
                        vpat.append(bc.Instr("LOAD_CONST", pat_core._v(v[0].arg[1])))
                    else:
                        vbind[v[0].arg] = args[i]
                        vpat.append(bc.Instr("LOAD_CONST", pat_core._v(v[0].arg)))
                else:
                    vpat.extend(v)
            vpat.append(mkTpl)
            lm, fvs = exprToLambda(expr, fn_name, filename, args, fv, vbind)
            parts.append((vpat, lm))
            free_vars.update(fvs)
    if not hasDefault:
        defaultExpr = generateDefault(fn_name, filename, args)
    defaultPat = []
    for _ in args:
        defaultPat.append(bc.Instr("LOAD_CONST", pat_core._v()))
    # if len(args) > 1:
    defaultPat.append(bc.Instr("BUILD_TUPLE", len(args)))
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        resbc = bc.Bytecode([bc.Instr("PUSH_NULL"), bc.Instr("PUSH_NULL"), bc.Instr("LOAD_CONST", pat_core.pytternd)])
    else:
        resbc = bc.Bytecode([bc.Instr("LOAD_CONST", pat_core.pytternd)])
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        for cell in free_vars:
            resbc.insert(0, bc.Instr("MAKE_CELL", bc.CellVar(cell)))
    for pat, expr in reversed(parts):
        resbc.extend(pat)
        resbc.extend(expr)
    resbc.extend(defaultPat)
    resbc.extend(defaultExpr)
    if not hasDefault:
        mk.arg += 1
    resbc.append(mk)
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        resbc.append(bc.Instr("PRECALL", 1))
        resbc.append(bc.Instr("CALL", 1))
    else:
        resbc.append(bc.Instr("CALL_FUNCTION", 1))
    for arg in args:
        resbc.append(bc.Instr("LOAD_FAST", arg))
    # if len(args) > 1:
    resbc.append(bc.Instr("BUILD_TUPLE", arg=len(args)))
    resbc.append(bc.Instr("BINARY_SUBSCR"))
    for arg in args:
        resbc.append(bc.Instr("LOAD_FAST", arg))
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        resbc.append(bc.Instr("PRECALL", arg=len(args)))
        resbc.append(bc.Instr("CALL", arg=len(args)))
    else:
        resbc.append(bc.Instr("CALL_FUNCTION", arg=len(args)))
    resbc.extend(case_inst.store.instrs)
    return resbc

@func
def handleCases(fn_name, filename, args, fv, instr):
    if not isinstance(instr, Case):
        return [instr]
    if mkConstMap(instr.body.insts[-1]):
        return transConstMap(instr, fn_name, filename, args, fv)
    elif mkMap(instr.body.insts[-1]):
        return transVarMap(instr, fn_name, filename, args, fv)

loadCase = and_(isLoadGlobal, __.arg ^ get1 == "case")

def extractGlobalName(i):
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        return bc.Instr("LOAD_FAST", i.arg[1])
    return bc.Instr("LOAD_FAST", i.arg)

globalName = ptrans(one(isLoadGlobal), trans0(trans0(extractGlobalName)))

parseCaseHead = ptrans(
    one(loadCase) >> many1(one(isArg) | globalName) << callInst,
    trans0(mp1(__.arg) ^ (lambda x: [CaseHead(x)])),
) 

parseStoreName = (
    ptrans(one(popTop), trans0(trans0(const(StoreName([bc.Instr("POP_TOP")])))))
    | ptrans(one(storeFast), trans0(lambda x: [StoreName(x)]))
    | ptrans(one(unpack) + many1(one(storeFast)), trans0(lambda x: [StoreName(x)]))
)

parseCaseBody = ptrans(
    many1(neg(or_(mkConstMap, mkMap))) + one(or_(mkConstMap, mkMap)) << callInst,
    trans0((lambda x: [CaseBody(x)])),
)
parseCase = many(parseCaseHead + parseCaseBody + parseStoreName | one(const(True)))

mergeCase = many(ptrans(
    one(is_(CaseHead)) + one(is_(CaseBody)) + one(is_(StoreName)),
    trans0((lambda x: [Case(*x)]))
    ) | one(const(True)))

@do(Just)
def deco(b, fn_name, filename, args, freevars):
    transBc <- (rightToMaybe(parseCase(b)) | get0)
    mergeCase <- (rightToMaybe(mergeCase(transBc)) | get0)
    return bc.Bytecode(sum(mp1(handleCases(fn_name, filename, args, freevars), mergeCase), start = []))


def case(fn):
    rawbc = bc.Bytecode.from_code(fn.__code__)
    argcount = fn.__code__.co_argcount + (1 if isVarargFn(fn) else 0)
    args = fn.__code__.co_varnames[:argcount]

    # print( f"Generating pattern matching for function: {fn.__name__} at line: {rawbc.first_lineno} @ {rawbc.filename}")
    resbc = deco(rawbc, fn.__name__, rawbc.filename, args, rawbc.freevars)
    assert isJust(
        resbc
    ), f"Failed to generate pattern matching for function: {fn.__name__} at line: {rawbc.first_lineno} @ {rawbc.filename}"
    res = fromJust(resbc)
    # print(f"{res = }")
    cells = set(rawbc.cellvars)
    for inst in res:
        if isInstr(inst) and inst.name == "MAKE_CELL":
            cells.add(inst.arg.name)
    res.freevars.extend(rawbc.freevars)
    res.cellvars.extend(cells)
    res.argcount = rawbc.argcount
    res.argnames.extend(rawbc.argnames)
    res.name = rawbc.name
    res.filename = rawbc.filename
    res.flags = rawbc.flags
    res.update_flags()
    fn.__code__ = res.to_code()
    # print("=" * 20)
    # dis.dis(fn)
    # dis.show_code(fn)
    # print("=" * 20)
    return fn

