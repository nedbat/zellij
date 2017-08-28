"""Test zellij/defuzz.py"""

import itertools
import math

from zellij.defuzz import Defuzzer
from zellij.postulates import all_pairs

from hypothesis import given, example
from hypothesis.strategies import integers, lists, tuples

from .hypo_helpers import f


def test_it():
    dfz = Defuzzer()
    assert dfz.defuzz((1, 2)) == (1, 2)
    assert dfz.defuzz((1, 3)) == (1, 3)
    assert dfz.defuzz((1.00000001, 2)) == (1, 2)
    assert dfz.defuzz((1, 2, 3, 4, 5)) == (1, 2, 3, 4, 5)
    assert dfz.defuzz((2.00000001, 3)) == (2.00000001, 3)
    assert dfz.defuzz((2, 3)) == (2.00000001, 3)


@given(lists(tuples(f, f)))
@example([(.48, 1.02), (.52, .98)])
def test_hypo(points):
    dfz = Defuzzer(ndigits=0)
    dfz_points = [dfz.defuzz(pt) for pt in points]

    # The output values should all be in the inputs.
    assert all(pt in points for pt in dfz_points)

    # No two unequal output values should be too close together.
    if len(points) > 1:
        for a, b in all_pairs(dfz_points):
            if a == b:
                continue
            distance = math.hypot(a[0] - b[0], a[1] - b[1])
            assert distance > .5


@given(
    start=f,
    ndigits=integers(min_value=-2, max_value=6),
    dimensions=integers(min_value=1, max_value=4),
)
def test_correct_distance(start, ndigits, dimensions):
    eps = 1e-10
    window = 10 ** -ndigits
    smallest_different = 1.5 * window + eps
    largest_same = 0.5 * window - eps
    step = 10.09 * window
    for i in range(10):
        num = start + i * step
        pt = (num,) * dimensions
        for signs in itertools.product([-1, 0, 1], repeat=dimensions):
            if all(s == 0 for s in signs):
                continue
            # Need a new defuzzer for each attempt, or previous "should be
            # different" points will be close to the "should be same" point.
            dfz = Defuzzer(ndigits=ndigits)
            assert dfz.defuzz(pt) == pt
            st = tuple(num + s * largest_same for s in signs)
            dfzst = dfz.defuzz(st)
            assert dfzst == pt
            dt = tuple(num + s * smallest_different for s in signs)
            dfzdt = dfz.defuzz(dt)
            assert dfzdt != pt
