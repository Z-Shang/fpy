from fpy.data.cont import Cont, cont
from fpy.data.forgetful import forget, Under
from fpy.composable.function import func

import unittest


add = lambda a, b: a + b
mul = lambda a, b: a * b
div = lambda a, b: a / b


class TestCont(unittest.TestCase):
    def testCont(self):
        ac = cont(add)
        mc = cont(mul)
        dc = cont(div)
        res = dc(2, 2) >> mc(3) >> ac(1)
        self.assertEqual(Under(4), res & forget)
        self.assertEqual(Under(2), ac(1, 1) & forget)

    def testContWithFunc(self):
        ac = cont(func(add))
        mc = cont(func(mul))
        dc = cont(func(div))
        res = dc(2, 2) >> mc(3) >> ac(1)
        self.assertEqual(Under(4), res & forget)
        self.assertEqual(Under(2), ac(1, 1) & forget)
