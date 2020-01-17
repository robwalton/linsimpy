import pytest
import simpy


# Not part of real code base! Just some experiments made while learning.

@pytest.fixture()
def env():
    return simpy.Environment()


def delayed_42(env):
    value = yield env.timeout(1, value=42)
    return value


def test_value_from_process(env: simpy.Environment):
    p = env.process(delayed_42(env))
    run_val = env.run()
    assert run_val is None
    assert p.value == 42
    assert env.now == 1


def test_value_from_run_call_with_process(env: simpy.Environment):
    # Also works for events
    proc = env.process(delayed_42(env))
    run_val = env.run(proc)
    assert run_val == 42


def test_value_from_subprocess(env: simpy.Environment):

    def proc():
        yield env.timeout(2)
        assert env.now == 2
        ret_val = yield env.process(delayed_42(env))
        assert env.now == 3
        assert ret_val == 42
        return ret_val * 2

    p = env.process(proc())
    run_val = env.run()
    assert run_val is None
    assert p.value == 84
    assert env.now == 3
