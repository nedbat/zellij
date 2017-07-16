import random

from hypothesis import given
from hypothesis.strategies import lists, randoms, composite

from euclid import Point
from hypo_helpers import points
from path_tiler import PathTiler, combine_paths


def test_do_nothing():
    pt = PathTiler()
    assert pt.paths == []


def test_two_segments():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.line_to(150, 200)
    pt.move_to(17, 17)
    pt.rel_line_to(100, 200)
    pt.close_path()
    assert pt.paths == [
        [Point(100.0, 100.0), Point(150.0, 200.0)],
        [Point(17.0, 17.0), Point(117.0, 217.0), Point(17.0, 17.0)],
    ]


def test_translation():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.translate(1000, 2000)
    pt.line_to(10, 20)
    assert pt.paths == [
        [Point(100.0, 100.0), Point(1010.0, 2020.0)],
    ]


def test_reflect_x():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.reflect_x(1000)
    pt.line_to(200, 200)
    assert pt.paths == [
        [Point(100.0, 100.0), Point(1800, 200)],
    ]


def test_reflect_y():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.reflect_y(1000)
    pt.line_to(200, 200)
    assert pt.paths == [
        [Point(100.0, 100.0), Point(200, 1800)],
    ]


def test_reflect_xy():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.reflect_xy(1000, 2000)
    pt.line_to(200, 200)
    assert pt.paths == [
        [Point(100.0, 100.0), Point(1800, 3800)],
    ]


def test_reflect_line():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.reflect_line(Point(50, -50), Point(150, 50))
    pt.line_to(100, 50)
    pt.line_to(100, 100)
    assert pt.paths == [
        [Point(100.0, 100.0), Point(150, 0), Point(200, 0)],
    ]


def test_save_restore():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.translate(1000, 2000)
    pt.line_to(10, 20)
    pt.save()
    pt.translate(1, 2)
    pt.move_to(1, 2)
    pt.line_to(2, 4)
    pt.restore()
    pt.move_to(1, 2)
    pt.line_to(2, 4)
    assert pt.paths == [
        [Point(100.0, 100.0), Point(1010.0, 2020.0)],
        [Point(1002.0, 2004.0), Point(1003.0, 2006.0)],
        [Point(1001.0, 2002.0), Point(1002.0, 2004.0)],
    ]


def test_rel_line_to():
    pt = PathTiler()
    pt.translate(1000, 2000)
    pt.move_to(0, 0)
    pt.rel_line_to(100, 200)
    assert pt.paths == [
        [Point(1000.0, 2000.0), Point(1100.0, 2200.0)],
    ]


def point_set(paths):
    """The set of points in all these paths."""
    return set(pt for path in paths for pt in path)

def num_segments(paths):
    """How many individual line segments are in these paths?"""
    return sum(len(p)-1 for p in paths)

@composite
def combinable_paths(draw):
    path_points = draw(lists(points, min_size=3, max_size=200, unique_by=tuple))
    rand = draw(randoms())

    paths = [[]]
    length = rand.randint(2, 4)
    for pt in path_points:
        paths[-1].append(pt)
        length -= 1
        if length == 0:
            paths.append([])
            length = rand.randint(2, 4)
            joinable = (rand.random() > .5)
            if joinable:
                paths[-1].append(pt)

    if len(paths[-1]) < 2:
        paths.pop()

    rand.shuffle(paths)
    return paths

@given(combinable_paths())
def test_combine_paths(paths):
    combined = combine_paths(paths)

    print(f"p: {paths}")
    print(f"c: {combined}")

    # Property: the points in the combined paths should all have been in the
    # original paths.
    assert point_set(paths) == point_set(combined)

    # Property: the combined paths should have no duplicate endpoints.
    endpoints = [path[i] for path in combined for i in [0, -1]]
    assert len(endpoints) == len(set(endpoints))

    # Property: the combined paths should have the same number of segments as
    # the original paths.
    assert num_segments(paths) == num_segments(combined)
