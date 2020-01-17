import pytest

import simpy

from linsimpy.simpy import ReadableFilterStore


@pytest.fixture()
def env():
    return simpy.Environment()


@pytest.fixture()
def store(env):
    return ReadableFilterStore(env)


def test_put(store: ReadableFilterStore, env):

    def pem():
        yield store.put((2,))
        yield store.put((1,))
    env.process(pem())
    env.run()
    assert store.items == [(2,), (1,)]


def test_get_put_put(store, env: simpy.Environment):

    def pem():
        get_event = store.get(lambda val: val == (1, ))
        yield store.put((2,))
        assert not get_event.triggered  # assert (1,) not found
        yield store.put((1,))
        assert get_event.triggered  # assert (1,)  found

    env.process(pem())
    env.run()
    assert store.items == [(2,)]  # assert (1,) removed and (2,) not removed


def test_read_put_put(store: ReadableFilterStore, env: simpy.Environment):

    def pem():
        rd_event = store.read(lambda val: val == (1, ))
        yield store.put((2,))
        assert not rd_event.triggered  # assert (1,) not found
        yield store.put((1,))
        assert rd_event.triggered  # assert (1,)  found

    env.process(pem())
    env.run()
    assert store.items == [(2,), (1,)]  # check only (1,) removed
