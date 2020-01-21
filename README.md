# linsimpy

[Linda](https://en.wikipedia.org/wiki/Linda_(coordination_language)) process
coordination on the [`simpy`](https://simpy.readthedocs.io) discrete event
simulation framework.

Linda is a long forgotten coordination language which at one point competed
conceptually with MPI. It is based on a bulletin-board like
[tuple-space](https://en.wikipedia.org/wiki/Tuple_space), not unlike a NoSQL
database in the style of associative memory, but which also hosts processes. It
does not stand up to today's approaches for engineering distributed systems, but
is great for modelling natural systems.  


## Software compatibility

Requires:
- python3+ (tested on 3.8 only to date)
- [simpy](https://gitlab.com/team-simpy/simpy)

## Installation
Check it out:
```bash
$ git clone https://github.com/robwalton/linsimpy.git
Cloning into 'linsimpy'...
```

## Try it out

This demo should abstract env away by using ts.eval() to spawn processes. It also
highlights that linsimpy needs a more clearly defined relationship with `simpy`.

Running:
```python

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
```
prints:
```
(1, 2) added at time 1
('three', 4) added at time 2
('three', 4) removed at time 2
(1, 2) removed at time 2
[('another tuple', 5, 6), ('producer_process', 'process can return something'), ('consumer_process', None)]

```

## Monitoring

If following simpy's [instructions] for patching Environment() to add event
tracing, do so on the simpy.Environment instance wrapped by
TupleSpaceEnvironment. This is done my passing a patched instance of
Environment to TupleSpaceEnvironment during initiation.



## Testing
Running the tests requires the `pytest` package. 

From the root package folder call:
```bash
$ pytest
...
```


## Licensing

The code and the documentation are released under the MIT and Creative Commons
Attribution-NonCommercial licences respectively. See LICENCE.md for details.

## TODO

- Package up
- Add instructions for setting random seed to guarantee order
- Possibly allow predicate functions as elements of search patterns. Adds no functionality
  but could help with conception, but does allow speed up if function calls are
  long as they may not need to be evaluated. Could help in the future if we add
  delays to gets().
- Optimise tuple searching. It is currently O(n). Suggestions from [lindypy].
  Wrap or extend Store of FilterStore to create TupleStore:
  - Keep a dict of tuples indexed by id. On put() assign tuple an id and add
    to this. (Note that this may require extension of Store rather than filterStore.)
  - Keep a column_index dict of sets indexed by tuple length. On put() put id in appropriate
    set.
  - Keep structure X comprised of: a list indexed by tuple element index holding
    dicts indexed by column value holding sets containing ids for each tuple.
    On put() add an entry for each element of the tuple.
  - on get(pattern) call onto a method that finds up to a certain number for
    future proofing. This:
    - return [] if length not length_index
    - take set of candidates from length_index
    - for each element in the pattern
      - if type: compile a list of type checks for wildcards
      - if iterable: optionally compile a list of predicate functions to test final candidates
        with.
      - else its a value:
        - if value not in column_index return []
        - trim the set of candidates by intersecting with set from structure X.
        - return [] if candidates is empty
    - return [] if candidates is empty (necessary?)
    - for each candidate
      - fetch the tuple from tuple_index
      -
- Create RealtimeTupleSpaceEnvironment
- Create a production, rather than DSE, tuple-store that spawns new processes.
  Possibly run on PyPy to get around GIL. It may be that going from Linda toys
  to production that it would best to switch technology and/or coordination
  paradigm




[instructions]: https://simpy.readthedocs.io/en/latest/topical_guides/monitoring.html#event-tracing
[lindypy]: (https://bitbucket.org/rfc1437/lindypy/src/default/lindypy/TupleSpace.py)
  
