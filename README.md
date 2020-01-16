# linsimpy

[Linda](https://en.wikipedia.org/wiki/Linda_(coordination_language)) process
coordination on the [`pysim`](https://simpy.readthedocs.io) discrete event
simulation framework.

Linda is a long forgotten coordination language which at one point competed
conceptually with MPI. It is based on a bulletin-board like
[tuple-space](https://en.wikipedia.org/wiki/Tuple_space), not unlike a NoSQL
database in the style of associative memory but which also hosts processes. It
does not stand up today's approaches for engineering distributed systems, but
is great for modelling natural systems.  


## Software compatibility

Requires:
- python3+ (tested on 3.8 only to date)
- [pysim](https://gitlab.com/team-simpy/simpy)

## Installation
Check it out:
```bash
$ git clone https://github.com/robwalton/lindes.git
Cloning into 'lindes'...
```

## Try it out

This demo should abstract env away by using ts.eval() to spawn processes. It also
highlights that linsimpy needs a more clearly defined relationship with `simpy`.

Running:
```python


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
```
prints:
```
(1, 2) added at time 1
('three', 4) added at time 2
('three', 4) removed at time 2
(1, 2) removed at time 2  
```



## Testing
Running the tests requires the `pytest` package. 

From the root package folder call:
```bash
$ pytest
...
```


## Licensing & thanks

The code and the documentation are released under the MIT and Creative Commons
Attribution-NonCommercial licences respectively. See LICENCE.txt for details.

## TODO

- Add the non blocking rd and in commands
- Consider API and encapsulation.
    - Consider option to make TupleSpace extend `simpy.Environment` to get run() etc.
    - Alternatively it suggest access via `ts.env`.



  
