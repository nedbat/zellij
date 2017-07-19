import itertools
import math

from defuzz import Defuzzer

from hypothesis import given
from hypothesis.strategies import floats, lists, tuples

from hypo_helpers import f


def test_it():
    dfz = Defuzzer()
    assert dfz.defuzz((1, 2)) == (1, 2)
    assert dfz.defuzz((1, 3)) == (1, 3)
    assert dfz.defuzz((1.00000001, 2)) == (1, 2)
    assert dfz.defuzz((1, 2, 3, 4, 5)) == (1, 2, 3, 4, 5)
    assert dfz.defuzz((2.00000001, 3)) == (2.00000001, 3)
    assert dfz.defuzz((2, 3)) == (2.00000001, 3)


@given(lists(tuples(f, f)))
def test_hypo(points):
    dfz = Defuzzer(round_digits=2)
    dfz_points = [dfz.defuzz(pt) for pt in points]

    # The output values should all be in the inputs.
    assert all(pt in points for pt in dfz_points)

    # No two unequal output values should be too close together.
    if len(points) > 1:
        for a, b in itertools.combinations(dfz_points, 2):
            if a == b:
                continue
            distance = math.hypot(a[0] - b[0], a[1] - b[1])
            assert distance > .01
