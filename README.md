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

[instructions]: https://simpy.readthedocs.io/en/latest/topical_guides/monitoring.html#event-tracing

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

- Support eval with multiple generators
- Add the non blocking rd and in commands
- Create RealtimeTupleSpaceEnvironment 




  
