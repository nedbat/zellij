import itertools
import math

from defuzz import Defuzzer

from hypothesis import given, example
from hypothesis.strategies import floats, integers, lists, tuples

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
#@example([(-9921.873619430073, -10000.0), (-9921.875, -9999.995194375517)])
#@example([(-992187.3619430073, -1000000.), (-992187.5, -999999.5194375517)])
# it only fails if the .5 is exactly .5:
@example([(-992187.3619430073, -1000000.), (-992187.5, -999999.5194375517)])
def test_hypo(points):
    dfz = Defuzzer(ndigits=0)
    dfz_points = [dfz.defuzz(pt) for pt in points]
    print(f"{points}\n{dfz_points}\n")

    # The output values should all be in the inputs.
    assert all(pt in points for pt in dfz_points)

    # No two unequal output values should be too close together.
    if len(points) > 1:
        for a, b in itertools.combinations(dfz_points, 2):
            if a == b:
                continue
            distance = math.hypot(a[0] - b[0], a[1] - b[1])
            assert distance > .5


@given(f, integers(min_value=-2, max_value=6))
def test_correct_distance(start, ndigits):
    dfz = Defuzzer(ndigits=ndigits)
    eps = 1e-10
    window = 10 ** -ndigits
    smallest_different = 1.5 * window + eps
    largest_same = 0.5 * window - eps
    step = 10 * window
    for i in range(20):
        num = start + i * step
        assert dfz.defuzz((num,)) == (num,)
        assert dfz.defuzz((num + largest_same,)) == (num,)
        assert dfz.defuzz((num - largest_same,)) == (num,)
        assert dfz.defuzz((num + smallest_different,)) != (num,)
        assert dfz.defuzz((num - smallest_different,)) != (num,)
