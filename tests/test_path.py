"""Test path.py"""

import collections
import math

from zellij.path import (
    combine_paths, equal_path, equal_paths, join_paths,
    paths_length, triple_points, clean_path,
)

from hypothesis import given
from hypothesis.strategies import lists, randoms, composite, one_of
import pytest

from zellij.euclid import collinear, Point

from .hypo_helpers import ipoints


@pytest.mark.parametrize("p1, p2, result", [
    ([Point(0, 0), Point(1, 1)], [Point(1, 1), Point(2, 0), Point(3, 0)],
            [Point(0, 0), Point(1, 1), Point(2, 0), Point(3, 0)]),
    ([Point(0, 0), Point(1, 1)], [Point(2, 2), Point(3, 3)],
            None),
    ([Point(0, 0), Point(1, 1)], [Point(1, 1), Point(2, 2), Point(3, 0)],
            [Point(0, 0), Point(2, 2), Point(3, 0)]),
])
def test_join_paths(p1, p2, result):
    def same(p1, p2):
        if p1 is None and p2 is None:
            return True
        elif p1 is None or p2 is None:
            return False
        else:
            return equal_path(p1, p2)
    assert same(join_paths(p1, p2), result)
    assert same(join_paths(p1[::-1], p2), result)
    assert same(join_paths(p1, p2[::-1]), result)
    assert same(join_paths(p1[::-1], p2[::-1]), result)


@pytest.mark.parametrize("path, result", [
    ([Point(0, 0), Point(0, 1), Point(0, 2)],
        [Point(0, 0), Point(0, 2)]),
    ([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)],
        [Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)]),
    ([Point(0, 0), Point(1, 0), Point(0, 1), Point(-1, 0), Point(0, 0)],
        [Point(-1, 0), Point(1, 0), Point(0, 1), Point(-1, 0)]),
])
def test_clean_path(path, result):
    assert equal_path(clean_path(path), result)


def point_set(paths):
    """The set of points in all these paths."""
    return set(pt for path in paths for pt in path)

def num_segments(paths):
    """How many individual line segments are in these paths?"""
    return sum(len(p)-1 for p in paths)

def endpoints(paths):
    """The list of endpoints of the paths."""
    # Be careful to preserve duplicates from different paths, but avoid them
    # in the same path.
    endpoints = []
    for path in paths:
        endpoints.append(path[0])
        if path[0] != path[-1]:
            endpoints.append(path[-1])
    return endpoints

@pytest.mark.parametrize("path, result", [
    ("abcde", ["abc", "bcd", "cde"]),
    ("abcdea", ["abc", "bcd", "cde", "dea", "eab"]),
    ("ab", []),
    ("abc", ["abc"]),
    ("aba", ["aba", "bab"]),
])
def test_triple_points(path, result):
    assert list("".join(them) for them in triple_points(list(path))) == result

def any_collinear(path):
    """Are any of the parts of this path collinear?"""
    return any(collinear(*them) for them in triple_points(path))

@composite
def combinable_paths_no_loops(draw):
    """Makes varying-length paths, but no loops."""
    path_points = draw(lists(ipoints, min_size=2, max_size=200, unique_by=tuple))
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

@composite
def combinable_paths_maybe_loops(draw):
    """Makes single-segment paths, with loops a possibility."""
    endpoints = draw(lists(ipoints, min_size=2, max_size=200, unique_by=tuple))
    rand = draw(randoms())
    paths = set()
    point_use = collections.defaultdict(int)

    target_number = len(endpoints) / 3
    if target_number < 1:
        target_number = 1

    while len(paths) < target_number:
        # Choose two points at random from the possible endpoints, and make a
        # segment.
        a, b = rand.sample(endpoints, k=2)
        if (a, b) in paths:
            continue
        paths.add((a, b))

        # Track how many times the points have been used.
        point_use[a] += 1
        point_use[b] += 1

        # Any point in two segments is no longer a candidate as an endpoint.
        if point_use[a] == 2:
            endpoints.remove(a)
        if point_use[b] == 2:
            endpoints.remove(b)

    return list(paths)

combinable_paths = one_of(combinable_paths_no_loops(), combinable_paths_maybe_loops())

@given(combinable_paths)
def test_combine_paths(paths):
    combined = combine_paths(paths)

    # Property: the points in the combined paths should all have been in the
    # original paths.
    assert point_set(paths) >= point_set(combined)

    # Property: the combined paths should have no duplicate endpoints.
    the_ends = endpoints(combined)
    assert len(the_ends) == len(set(the_ends))

    # Property: the combined paths should have the same or fewer segments as
    # the original paths.
    assert num_segments(paths) >= num_segments(combined)

    # Property: the combined paths should have the same total length as the
    # original paths.
    assert math.isclose(paths_length(paths), paths_length(combined))

    # Property: there should be no collinear triples in any path.
    assert not any(any_collinear(path) for path in combined)

@given(combinable_paths)
def test_combine_paths_recursive(paths):
    # We can combine the paths in two halves, then combine the halves, and get
    # the same results as combining them all at once.
    combined_all_at_once = combine_paths(paths)

    combined_evens = combine_paths(paths[0::2])
    combined_odds = combine_paths(paths[1::2])
    combined_in_halves = combine_paths(combined_evens + combined_odds)

    assert equal_paths(combined_all_at_once, combined_in_halves)
