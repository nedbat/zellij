"""
Test euclid.py
"""

import math

from hypothesis import given
from hypothesis.strategies import floats, tuples
import pytest

from euclid import BadGeometry, collinear, Line, Point


# Points

@pytest.mark.parametrize("p1, p2, result", [
    ((0, 0), (0, 0), True),
    ((0, 0), (1, 0), False),
    ((0, 0), (0.000000001, 0), True),
    ((0, 0), (0.001, 0), False),
])
def test_point_equality(p1, p2, result):
    assert (Point(*p1) == Point(*p2)) == result

@pytest.mark.parametrize("p1, p2, result", [
    ((0, 0), (1, 1), 1.4142135623730951),
    ((10, 10), (10, 10), 0),
    ((100, 100), (103, 104), 5),
])
def test_point_distance(p1, p2, result):
    assert math.isclose(Point(*p1).distance(Point(*p2)), result)

@pytest.mark.parametrize("p1, p2, p3, result", [
    ((0, 0), (1, 1), (10, 10), True),
    ((0, 0), (1, 1), (100, 200), False),
    ((0, 0), (1, 1), (1000000, 1000001), False),
    ((0, 0), (1, 1), (10.000000001, 10), True),
])
def test_points_collinear(p1, p2, p3, result):
    assert collinear(Point(*p1), Point(*p2), Point(*p3)) == result


f = floats(min_value=-1000000, max_value=1000000, allow_nan=False, allow_infinity=False)

@given(
    tuples(f, f), tuples(f, f), f.filter(lambda f: abs(f) > 1e-8)
)
def test_hypo_points_collinear(p1, p2, t):
    # If I pick a point that is a linear combination of two points, it should
    # be considered collinear.
    p1 = Point(*p1)
    p2 = Point(*p2)
    p3 = Point(p1.x + (p2.x - p1.x) * t, p1.y + (p2.y - p1.y) * t)
    assert collinear(p1, p2, p3)


# Lines

@pytest.mark.parametrize("p1, p2, p3, p4, pi", [
    ((-1, 0), (1, 0),  (0, -1), (0, 1),  (0, 0)),
    ((17, 34), (23, 42),   (100, 200), (300, 350),  (194.85714285, 271.14285714)),
])
def test_intersect(p1, p2, p3, p4, pi):
    l1 = Line(Point(*p1), Point(*p2))
    l2 = Line(Point(*p3), Point(*p4))
    assert l1.intersect(l2) == Point(*pi)


@pytest.mark.parametrize("p1, p2, p3, p4", [
    # Two identical lines.
    ((-1, 0), (1, 0),  (-1, 0), (1, 0)),
    # Two parallel lines.
    ((-1, 0), (1, 0),  (-2, 0), (2, 0)),
])
def test_no_intersection(p1, p2, p3, p4):
    l1 = Line(Point(*p1), Point(*p2))
    l2 = Line(Point(*p3), Point(*p4))
    with pytest.raises(BadGeometry):
        l1.intersect(l2)


def test_offset():
    l1 = Line(Point(10, 10), Point(13, 14))
    l2 = l1.offset(10)
    assert l2.p1 == Point(18, 4)
    assert l2.p2 == Point(21, 8)
