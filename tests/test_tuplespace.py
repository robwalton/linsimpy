from linsimpy.tuplespace import TupleFilter, TupleSpaceEnvironment
import simpy

import pytest


COMPLETE = None


@pytest.fixture()
def tse():
    return TupleSpaceEnvironment(simpy.Environment())


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


def test_out(tse):

    def pem():
        yield tse.out((2,))
        yield tse.out((1,))
    tse.run(tse.eval((pem(),)))
    assert tse.items == [(2,), (1,), (None,)]  # where (None,) is left by eval


def test_out_out_in(tse):

    def pem():
        get_event = tse.in_((1, ))
        yield tse.out((2,))
        assert not get_event.triggered  # assert (1,) not found
        yield tse.out((1,))
        assert get_event.triggered  # assert (1,)  found

    tse.run(tse.eval((pem(),)))
    assert tse.items == [(2,), (None,)]


def test_in_removes_just_one_duplicated_tuple(tse):

    def pem():
        tse.in_((1, ))
        yield tse.out((1,))
        yield tse.out((1,))

    tse.run(tse.eval((pem(),)))
    assert tse.items == [(1,), (None,)]  # check only (1,) removed
    assert not tse.active_process


def test_in_when_used_in_run_returns_tuple(tse):

    tse.items.append((1,))

    def pem():
        val = yield tse.in_((1,))
        return val
    assert tse.run(tse.eval((pem(),))) == ((1,),)


def test_out_out_rd(tse):

    def pem():
        rd_event = tse.rd((1, ))
        yield tse.out((2,))
        assert not rd_event.triggered  # assert (1,) not found
        yield tse.out((1,))
        assert rd_event.triggered  # assert (1,)  found

    tse.run(tse.eval((pem(),)))
    assert tse.items == [(2,), (1,), (None,)]


def test_rdp(tse):
    tse.items.append((1, 2))
    assert tse.rdp((1, object)) == (1, 2)
    assert tse.items == [(1, 2)]


def test_rdp_raises_key_error(tse):
    tse.items.append((1, 2))
    with pytest.raises(KeyError):
        tse.rdp((1, 'not in tuple-space'))
    assert tse.items == [(1, 2)]


def test_inp(tse):
    tse.items.append((1, 2))
    assert tse.inp((1, object)) == (1, 2)
    assert tse.items == []


def test_inp_raises_key_error(tse):
    tse.items.append((1, 2))
    with pytest.raises(KeyError):
        tse.inp((1, 'not in tuple-space'))
    assert tse.items == [(1, 2)]


def delayed_42(tse):
    value = yield tse.timeout(1, value=42)
    return value


def delayed_24(tse):
    value = yield tse.timeout(1, value=24)
    return value


def test_eval(tse):

    def mep():
        yield tse.eval((1, delayed_42(tse)))
        assert tse.now == 1
        return 'mep done'

    assert tse.run(tse.eval((mep(),))) == ('mep done',)
    assert tse.items == [(1, 42), ('mep done',)]


def test_eval_with_multiple_generators(tse):

    def mep():
        yield tse.eval(('one', delayed_42(tse), 2, delayed_24(tse)))
        assert tse.now == 1  # should occur concurrently
        return 'mep done'

    assert tse.run(tse.eval((mep(),)))
    assert tse.items == [('one', 42, 2, 24), ('mep done',)]


def test__str__(tse):
    print()
    tse.items.append(('a', 'b(\n  1,\n  2\n)', 'c'))
    print(tse)


def test_readme_example():

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
        yield tse.out(('another tuple', 5, 6))

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

