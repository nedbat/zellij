from euclid import Point
from pointmap import PointMap


def test_empty_pointmap():
    pm = PointMap(list)
    assert len(pm) == 0
    assert list(pm) == []
    assert Point(1, 2) not in pm


def test_adding():
    pm = PointMap(list)
    pm[Point(1, 2)].append(47)
    assert pm[Point(1, 2)] == [47]
    pm[Point(1, 2)].append(123)
    assert pm[Point(1, 2)] == [47, 123]
    assert Point(1, 2) in pm
    assert len(pm) == 1
    assert list(pm) == [Point(1, 2)]
    assert list(pm.items()) == [(Point(1, 2), [47, 123])]


def test_inexact_adding():
    pm = PointMap(list)
    pm[Point(1, 2)].append(47)
    pm[Point(1.000000001, 2)].append(123)
    assert pm[Point(1, 2)] == [47, 123]
    assert Point(1, 2.000000001) in pm
    assert len(pm) == 1
    assert list(pm) == [Point(1, 2)]
    assert list(pm.items()) == [(Point(1, 2), [47, 123])]


def test_multiple_adding():
    pm = PointMap(list)
    pm[Point(1, 2)].append(47)
    pm[Point(2, 3)].append(123)
    assert len(pm) == 2
    assert list(pm) == [Point(1, 2), Point(2, 3)]
    assert list(pm.items()) == [(Point(1, 2), [47]), (Point(2, 3), [123])]
