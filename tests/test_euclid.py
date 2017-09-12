"""
Test euclid.py
"""

import itertools
import math

from hypothesis import assume, given
from hypothesis.strategies import lists, integers
import pytest

from zellij.euclid import (
    Line, Point, Segment, Bounds,
    along_the_way, collinear, line_collinear,
    CoincidentLines, ParallelLines,
)
from zellij.postulates import adjacent_pairs, all_pairs

from .hypo_helpers import ipoints, t_zero_one


# Points

@pytest.mark.parametrize("p1, p2, result", [
    ((0, 0), (0, 0), True),
    ((0, 0), (1, 0), False),
    ((0, 0), (0.000000001, 0), False),
    ((0, 0), (0.001, 0), False),
])
def test_point_equality(p1, p2, result):
    assert (Point(*p1) == Point(*p2)) == result

@pytest.mark.parametrize("p1, p2, result", [
    ((0, 0), (0, 0), True),
    ((0, 0), (1, 0), False),
    ((0, 0), (0.000000001, 0), True),
    ((0, 0), (0.001, 0), False),
])
def test_point_is_close(p1, p2, result):
    assert Point(*p1).is_close(Point(*p2)) == result

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
    ((131.1614964698457, -376.12499999999994), (131.16149646984576, -404.17837588253866), (131.16149646984567, -363.1644750675048), False),
    ((131.16149646984576, -404.17837588253866), (131.1614964698457, -376.12499999999994), (131.16149646984567, -363.1644750675048), True),
])
def test_points_collinear(p1, p2, p3, result):
    assert collinear(Point(*p1), Point(*p2), Point(*p3)) == result


@given(ipoints, ipoints, t_zero_one)
def test_hypo_points_collinear(p1, p2, t):
    # If I pick a point that is a linear combination of two points, it should
    # be considered collinear. The value of t determines in what order the
    # points are collinear.  We check for not-collinear, but only if t is away
    # from the fuzzy areas near zero and one, and if p1 and p2 are separated.
    p3 = along_the_way(p1, p2, t)
    if t < 0:
        assert collinear(p3, p1, p2)
        if t < 0.01 and p1 != p2:
            assert not collinear(p1, p3, p2)
            assert not collinear(p1, p2, p3)
    elif t <= 1:
        assert collinear(p1, p3, p2)
        if 0.01 < t < 0.99 and p1 != p2:
            assert not collinear(p3, p1, p2)
            assert not collinear(p1, p2, p3)
    else:
        assert collinear(p1, p2, p3)
        if t > 1.01 and p1 != p2:
            assert not collinear(p3, p1, p2)
            assert not collinear(p1, p3, p2)

@given(ipoints, ipoints, t_zero_one)
def test_hypo_points_not_collinear(p1, p2, t):
    # If I pick a point that is a linear combination of two points, it should
    # not be considered collinear with a line that is offset from the two points.
    if p1.distance(p2) < 1:
        # If the endpoints are too close together, the floats get unwieldy.
        return
    p3 = along_the_way(p1, p2, t)
    next_to = Line(p1, p2).offset(1)
    p1o, p2o = next_to.p1, next_to.p2
    assert not collinear(p1o, p2o, p3)


# Lines

@pytest.mark.parametrize("p1, p2, angle", [
    ((0, 0), (1, 0), 0),
    ((0, 0), (0, 1), 90),
    ((10, 10), (0, 20), 135),
])
def test_line_angle(p1, p2, angle):
    l = Line(Point(*p1), Point(*p2))
    assert math.isclose(l.angle(), angle)


@pytest.mark.parametrize("p1, p2, p3, p4, pi", [
    ((-1, 0), (1, 0),  (0, -1), (0, 1),  (0, 0)),
    ((17, 34), (23, 42),   (100, 200), (300, 350),  (194.85714285, 271.14285714)),
])
def test_intersect(p1, p2, p3, p4, pi):
    l1 = Line(Point(*p1), Point(*p2))
    l2 = Line(Point(*p3), Point(*p4))
    assert l1.intersect(l2).is_close(Point(*pi))


@pytest.mark.parametrize("p1, p2, p3, p4, err", [
    # Two identical lines.
    ((-1, 0), (1, 0),  (-1, 0), (1, 0),  CoincidentLines),
    ((-1, 0), (1, 0),  (-2, 0), (2, 0),  CoincidentLines),
    # Two parallel lines.
    ((-1, 0), (1, 0),  (-2, 1), (2, 1),  ParallelLines),
])
def test_no_intersection(p1, p2, p3, p4, err):
    l1 = Line(Point(*p1), Point(*p2))
    l2 = Line(Point(*p3), Point(*p4))
    with pytest.raises(err):
        l1.intersect(l2)


def test_offset():
    l1 = Line(Point(10, 10), Point(13, 14))
    l2 = l1.offset(10)
    assert l2.p1 == Point(18, 4)
    assert l2.p2 == Point(21, 8)


@given(ipoints, ipoints, ipoints)
def test_parallel(p1, p2, p3):
    # Make a line, and another line parallel to it through p3.
    l = Line(p1, p2)
    lpar = l.parallel(p3)

    # Property: lpar should go through p3.
    assert lpar.p1 == p3

    # Property: l and lpar should have the same angle.
    assert lpar.angle() == l.angle()

@given(ipoints, ipoints, ipoints)
def test_perpendicular(p1, p2, p3):
    assume(p1 != p2)
    l = Line(p1, p2)
    foot = l.foot(p3)
    perp = l.perpendicular(p3)
    print(foot)
    print(perp)

    # Property: foot should be on l.
    assert line_collinear(p1, p2, foot)

    # Property: foot should be on perp.
    assert line_collinear(perp.p1, perp.p2, foot)

    # Property: perp's angle should be 90 degrees from l's.
    angle_between = l.angle() - perp.angle()
    assert math.isclose(angle_between % 180, 90)


# Segments

SEGMENT_INTERSECTIONS = [
    # Good intersection.
    ((0, 1), (2, 1),  (1, 0), (1, 2),  (1, 1)),
    # lines intersect, but segments don't.
    ((0, 1), (2, 1),  (1, 2), (1, 4),  None),
    ((0, 1), (2, 1),  (3, 0), (3, 2),  None),
    ((1, 2), (1, 4),  (3, 1), (5, 1),  None),
    # lines are parallel.
    ((0, 1), (2, 1),  (1, 3), (3, 3),  None),
    # lines are coincident, segments don't overlap.
    ((0, 1), (2, 1),  (3, 1), (5, 1),  None),
]

@pytest.mark.parametrize("p1, p2, p3, p4, isect", SEGMENT_INTERSECTIONS)
def test_segment_intersection(p1, p2, p3, p4, isect):
    seg12 = Segment(p1, p2)
    seg34 = Segment(p3, p4)
    assert seg12.intersect(seg34) == isect

@pytest.mark.parametrize("p1, p2, p3, p4, isect", SEGMENT_INTERSECTIONS)
def test_segment_touches(p1, p2, p3, p4, isect):
    seg12 = Segment(p1, p2)
    seg34 = Segment(p3, p4)
    if isect is None:
        assert not seg12.touches(seg34)
    else:
        assert seg12.touches(seg34)


SEGMENT_INTERSECTION_ERRORS = [
    # lines are coincident, segments do overlap.
    ((0, 1), (2, 1),  (1, 1), (3, 1),  CoincidentLines),
    ((1, -5), (-1, -5), (-5, -5), (0, -5),  CoincidentLines),
]

@pytest.mark.parametrize("p1, p2, p3, p4, err", SEGMENT_INTERSECTION_ERRORS)
def test_segment_intersect_error(p1, p2, p3, p4, err):
    with pytest.raises(err):
        assert Segment(p1, p2).intersect(Segment(p3, p4))

@pytest.mark.parametrize("p1, p2, p3, p4, err", SEGMENT_INTERSECTION_ERRORS)
def test_segment_touches_errors(p1, p2, p3, p4, err):
    assert err == CoincidentLines   # ick
    assert Segment(p1, p2).touches(Segment(p3, p4))


@given(ipoints, ipoints, lists(integers(min_value=1, max_value=99), min_size=1, max_size=5, unique=True))
def test_segment_sort_along(p1, p2, tvals):
    # Get rid of pathological cases.
    assume(p1.distance(p2) > 0.001)

    tvals = [t / 100 for t in tvals]
    fuzz = [1e-10, -1e-10]
    points = [along_the_way(p1, p2, t) for t in tvals]
    points = [Point(x+f, y+f) for (x, y), f in zip(points, itertools.cycle(fuzz))]

    # Calculate the smallest distance between any pair of points.  If we get
    # the wrong answer from sort_along, then the total distance will be off by
    # at least twice this.
    min_gap = min(q1.distance(q2) for q1, q2 in all_pairs(points + [p1, p2]))

    seg = Segment(p1, p2)
    spoints = seg.sort_along(points)

    assert len(spoints) == len(points)
    assert all(pt in points for pt in spoints)

    original = Point(*p1).distance(Point(*p2))
    total = (
        Point(*p1).distance(Point(*spoints[0])) +
        sum(Point(*p).distance(Point(*q)) for p, q in adjacent_pairs(spoints)) +
        Point(*spoints[-1]).distance(Point(*p2))
    )
    # The total distance will be wrong by at least 2*min_gap if it is wrong.
    assert total - original < 2 * min_gap


# Bounds

@given(lists(ipoints, min_size=1))
def test_bounds_points(pts):
    bounds = Bounds.points(pts)
    assert_good_bounds(bounds, pts)


def assert_good_bounds(bounds, pts):
    """Assert that `bounds` is the right bounds for `pts`."""
    assert bounds.llx <= bounds.urx
    assert bounds.lly <= bounds.ury

    # The bounds must contain all the points.
    assert all(bounds.llx <= pt.x <= bounds.urx for pt in pts)
    assert all(bounds.lly <= pt.y <= bounds.ury for pt in pts)

    # Each edge of the bounds must touch at least one point.
    assert any(bounds.llx == pt.x for pt in pts)
    assert any(bounds.lly == pt.y for pt in pts)
    assert any(bounds.urx == pt.x for pt in pts)
    assert any(bounds.ury == pt.y for pt in pts)


@given(lists(ipoints, min_size=2))
def test_bounds_union(pts):
    # Compute the bounds of the even and odd separately.
    b0 = Bounds.points(pts[::2])
    b1 = Bounds.points(pts[1::2])

    # The union should be correct.
    b = b0 | b1

    assert_good_bounds(b, pts)


@given(lists(ipoints, min_size=4, max_size=8, unique=True))
def test_bounds_overlap(pts):
    b0 = Bounds.points(pts[::2])
    b1 = Bounds.points(pts[1::2])
    assume(b0.width > 0 and b0.height > 0)
    assume(b1.width > 0 and b1.height > 0)
    assume(b0 != b1)

    print(b0, b1)
    if b0.overlap(b1):
        # If they overlap, then one of the corners of b0 must be in b1,
        # or vice-versa, or the side Segments must touch.
        b0_in_b1 = any(pt in b1 for pt in b0.corners())
        b1_in_b0 = any(pt in b0 for pt in b1.corners())
        sides0 = list(b0.sides())
        sides1 = list(b1.sides())
        sides_touch = any(s0.touches(s1) for s0 in sides0 for s1 in sides1)
        assert b0_in_b1 or b1_in_b0 or sides_touch
    else:
        # If they don't overlap, then none of the corners is in the other.
        assert not any(pt in b1 for pt in b0.corners())
        assert not any(pt in b0 for pt in b1.corners())
