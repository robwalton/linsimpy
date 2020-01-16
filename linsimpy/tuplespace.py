import types
from typing import Tuple

import simpy

from linsimpy.simpy import ReadableFilterStore


class TupleFilter(object):

    def __init__(self, pattern: Tuple):
        self.pattern = pattern

    def __call__(self, tup: Tuple):

        # check length
        if not len(tup) == len(self.pattern):
            return False

        # check each element of tuples
        for tup_val, pattern_val in zip(tup, self.pattern):

            # check tup value against formal type placeholders in pattern
            if isinstance(pattern_val, type):
                if not isinstance(tup_val, pattern_val):
                    return False
            # otherwise check for equality
            else:
                if not tup_val == pattern_val:
                    return False

        return True


class TupleSpace(object):
    """A tuple-space implementation based on the Linda coordination language.

    Supports duplicate tuples.


    """

    def __init__(self, env: simpy.Environment = None):
        self.env = env if env else simpy.Environment()
        self.store = ReadableFilterStore(self.env)

    @property
    def items(self):
        """Return all tuples in store"""
        return self.store.items

    def out(self, tup: Tuple):
        """Returns a simpy event which writes a tuple"""
        return self.store.put(tuple(tup))

    def in_(self, tup: Tuple):
        """Returns a simpy event which atomically reads and and removes a tuple,
        waiting if necessary.
        """
        return self.store.get(TupleFilter(tup))

    def rd(self, tup: Tuple):
        """Returns a simpy event which non-destructively reads a tuple,
        waiting if necessary.
        """
        filter_store_get_event = self.store.read(TupleFilter(tup))
        return filter_store_get_event

    def eval(self, tup: Tuple):
        """Returns a simpy process which evaluates tuples with simpy style
        generator methods describing the process as elements. Adds the tuple
        to the tuple-space when complete"""

        process_list = []
        for i, element in enumerate(tup):
            if isinstance(element, types.GeneratorType):
                process_list.append((i, element))
        if not process_list:
            raise TypeError('no process (in the form of a generator in input tuple')

        def eval_process():
            assert len(process_list) == 1  # Only one element supported so far
            idx, proc = process_list[0]
            val = yield self.env.process(proc)
            tup_as_list = list(tup)
            tup_as_list[idx] = val
            yield self.out(tuple(tup_as_list))

        return self.env.process(eval_process())

    def inp(self, tup: Tuple):
        """Atomically reads and removes—consumes—a tuple, raising KeyError if
        not found. """
        raise NotImplemented()

    def rdp(self, tup: Tuple):
        """Non-destructively reads a tuple, raising KeyError if not found."""
        raise NotImplemented()
        # may have to inp and out without yielding control
