from build.lib.fpy.data.state import execState
from fpy.data.state import State, runState, put, get, modify, gets, evalState
from fpy.data.function import const
from fpy.composable.function import func
from fpy.composable.collections import get1

from fpy.experimental.do import do

import unittest

class TestState(unittest.TestCase):
    def testRet(self):
        r = runState(State.ret('X'), 1)
        self.assertEqual(('X', 1), r)
    
    def testGet(self):
        r = runState(get(), 1)
        self.assertEqual((1, 1), r)
    
    def testPut(self):
        r = runState(put(5), 1)
        self.assertEqual((None, 5), r)

    def testModify(self):
        r = runState(modify(lambda x: x + 1), 1)
        self.assertEqual((None, 2), r)

    def testPlay(self):
        # Example from: https://wiki.haskell.org/State_Monad
        # GameState = (Bool, Int)
        def play(chars):
            if chars == []:
                return gets(get1) >> State.ret

            @func
            def case(c, st):
                o, s = st
                if c == 'a' and o:
                    return put((o, s + 1))
                elif c == 'b' and o:
                    return put((o, s - 1))
                elif c == 'c':
                    return put((not o, s))
                else:
                    return put((o, s))

            x, *xs = chars

            return get() >> case(x) >> const(play(xs))

        r = evalState(play("abcaaacbbcabbab"), (False, 0))
        self.assertEqual(2, r)

    def testDo(self):
        @do(State)
        def test():
            s <- get()
            put(s + 1)
            modify(lambda x: x * 2)

        r = execState(test(), 1)
        self.assertEqual(4, r)

    def testPlayDo(self):
        # Example from: https://wiki.haskell.org/State_Monad
        # GameState = (Bool, Int)
        @do(State)
        def play(chars):
            (o, s) <- get()
            if chars == []:
                return s

            @func
            def case(c, o, s):
                if c == 'a' and o:
                    return put((o, s + 1))
                elif c == 'b' and o:
                    return put((o, s - 1))
                elif c == 'c':
                    return put((not o, s))
                else:
                    return put((o, s))

            x, *xs = chars

            case(x, o, s)
            play(xs)

        r = evalState(play("abcaaacbbcabbab"), (False, 0))
        self.assertEqual(2, r)
