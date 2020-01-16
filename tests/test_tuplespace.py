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


def test_playground_for_doc_using_tse():

    import linsimpy
    tse = linsimpy.TupleSpaceEnvironment()
    print()

    def producer():
        yield tse.timeout(1)
        print(f"(1, 2) added at time {tse.now}")
        yield tse.out((1, 2))

        yield tse.timeout(1)
        print(f"('three', 4) added at time {tse.now}")
        yield tse.out(('three', 4))

        return 'process can return something'

    def consumer():
        val = yield tse.in_(('three', int))
        print(f"{val} removed at time {tse.now}")

        val = yield tse.in_((object, 2))
        print(f"{val} removed at time {tse.now}")

    tse.eval(('producer_process', producer()))
    tse.eval(('consumer_process', consumer()))
    tse.run()
    assert tse.now == 2
    print(tse.items)


