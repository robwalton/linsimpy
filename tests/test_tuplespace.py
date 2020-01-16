import linsimpy
from linsimpy.tuplespace import TupleFilter, TupleSpace
import simpy

import pytest


COMPLETE = None


@pytest.fixture()
def env():
    return simpy.Environment()


@pytest.fixture()
def ts(env):
    return TupleSpace(env)


class C(object):
    pass


class TestTupleFilter(object):

    def test_equal_numbers(self):
        tf = TupleFilter((1, 2, 3))
        assert tf((1, 2, 3))

    def test_equal_single(self):
        tf = TupleFilter(('s',))
        assert tf(('s',))

    def test_equal_kitchen_sink(self):
        o = object()
        c = C()
        tf = TupleFilter(('a', 1, o, c))
        assert tf(('a', 1, o, c))

    def test_wrong_length(self):
        tf = TupleFilter((1, 2, 3))
        assert not tf((1, 2))

    def test_wrong_type(self):
        tf = TupleFilter((1, str))
        assert not tf((1, 2))

    def test_wrong_numbers(self):
        tf = TupleFilter((1, 2, 3))
        assert not tf((1, 2, 4))

    def test_wrong_single_value(self):
        tf = TupleFilter(('s',))
        assert not tf(('x',))

    def test_wrong_kitchen_sink(self):
        o = object()
        c = C()
        tf = TupleFilter(('a', 1, o, c))
        assert not tf(('a', 2, o, c))


def test_out(ts, env):

    def pem():
        yield ts.out((2,))
        yield ts.out((1,))
    env.process(pem())
    env.run()
    assert ts.items == [(2,), (1,)]


def test_out_out_in(ts, env: simpy.Environment):

    def pem():
        get_event = ts.in_((1, ))
        yield ts.out((2,))
        assert not get_event.triggered  # assert (1,) not found
        yield ts.out((1,))
        assert get_event.triggered  # assert (1,)  found

    env.process(pem())
    env.run()
    assert ts.items == [(2,)]  # assert (1,) removed and (2,) not removed


def test_in_reads_just_one_tuple(ts, env: simpy.Environment):

    def pem():
        get_event = ts.in_((1, ))
        yield ts.out((1,))
        yield ts.out((1,))

    env.process(pem())
    env.run()
    assert ts.items == [(1,)]  # assert (1,) removed and (2,) not removed
    assert not env.active_process


def test_out_out_rd(ts, env: simpy.Environment):

    def pem():
        rd_event = ts.rd((1, ))
        yield ts.out((2,))
        assert not rd_event.triggered  # assert (1,) not found
        yield ts.out((1,))
        assert rd_event.triggered  # assert (1,)  found

    env.process(pem())
    env.run()
    assert ts.items == [(2,), (1,)]  # assert (1,) removed and (2,) not removed


def delayed_42(env):
    value = yield env.timeout(1, value=42)
    return value


def test_eval_and_in_actual_value(env, ts):
    global COMPLETE
    COMPLETE = False

    def waiter():
        global COMPLETE
        tup = (1, delayed_42(env))
        yield ts.eval(tup)
        assert env.now == 1
        val = yield ts.in_((1, 42))
        assert val == (1, 42)
        COMPLETE = True

    env.process(waiter())
    env.run()

    assert COMPLETE


def test_eval_and_in_with_placeholder(ts: TupleSpace, env):

    def waiter():
        yield ts.eval((1, delayed_42(env)))
        val = yield ts.in_((1, object))
        return val

    assert env.run(env.process(waiter())) == (1, 42)


def test_playground_for_doc():

    # This demo should abstract env away by using ts.eval() to spawn processes

    import simpy
    import linsimpy
    env = simpy.Environment()
    ts = linsimpy.TupleSpace(env)
    print()

    def producer():
        yield env.timeout(1)
        print(f"(1, 2) added at time {env.now}")
        yield ts.out((1, 2))

        yield env.timeout(1)
        print(f"('three', 4) added at time {env.now}")
        yield ts.out(('three', 4))

    def consumer():
        val = yield ts.in_(('three', int))
        print(f"{val} removed at time {env.now}")

        val = yield ts.in_((object, 2))
        print(f"{val} removed at time {env.now}")

    env.process(producer())
    env.process(consumer())
    env.run()

    # (1, 2) added at time 1
    # ('three', 4) added at time 2
    # ('three', 4) removed at time 2
    # (1, 2) removed at time 2








#     def testSimple(self):
#         from lindes.TupleSpace import TSpace
#         ts = TSpace()
#         ts.add((1,2,3,4))
#         self.assertEqual(ts.values(), [(1,2,3,4)])
#         self.assertEqual(ts.get((1,2,3,4)), (1,2,3,4))
#         self.assertRaises(KeyError, ts.get, ((2,3,3,4),))
#
#     def testSimpleRemove(self):
#         from lindes.TupleSpace import TSpace
#         ts = TSpace()
#         ts.add((1,2,3,4))
#         self.assertEqual(ts.values(), [(1,2,3,4)])
#         self.assertEqual(ts.get((1,2,3,4), remove=True), (1,2,3,4))
#         self.assertRaises(KeyError, ts.get, ((2,3,3,4),))
#
#     def testPatterns(self):
#         from lindes.TupleSpace import TSpace
#         ts = TSpace()
#         ts.add((1,2,3,4))
#         self.assertEqual(ts.values(), [(1,2,3,4)])
#         self.assertEqual(ts.get((object,object,object,object)), (1,2,3,4))
#         self.assertRaises(KeyError, ts.get, ((object,object,object,object,object),))
#
#     def testComplexPatterns(self):
#         from lindes.TupleSpace import TSpace
#         ts = TSpace()
#         ts.add((1,2,3,4))
#         ts.add((5,2,3,7))
#         ts.add((1,2,3,4,5,6))
#         self.assertEqual(ts.get((object,2,3,object)), (1,2,3,4))
#         self.assertEqual(ts.get((5,object,3,object)), (5,2,3,7))
#         self.assertEqual(ts.get((1,2,object,object,5,object)), (1,2,3,4,5,6))
#         self.assertRaises(KeyError, ts.get, ((7,6,object,object,object,object),))
#
#     def testFuncPatterns(self):
#         from lindes.TupleSpace import TSpace
#
#         def match_even(x):
#             return x%2 == 0
#
#         def match_odd(x):
#             return x%2 == 1
#
#         ts = TSpace()
#         ts.add((2,1,4))
#         ts.add((1,3,6))
#         self.assertRaises(KeyError, ts.get, ((match_even,match_even,match_even),))
#         self.assertEqual(ts.get((match_even,match_odd,match_even)), (2,1,4))
#         self.assertEqual(ts.get((match_odd,match_odd,match_even)), (1,3,6))