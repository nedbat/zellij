import math
import os.path
import sys
import unittest

from hypothesis import given
from hypothesis.strategies import builds, lists, integers, tuples

from zellij.euclid import collinear
from zellij.intersection import segment_intersections


nums = integers(min_value=-10000, max_value=10000)
points = tuples(nums, nums)
segments = builds(tuple, lists(points, min_size=2, max_size=2, unique=True))

@given(lists(segments, min_size=2, max_size=100, unique=True))
def test_intersections(segments):
    isects = segment_intersections(segments)
    for pt, segs in isects.items():
        for seg in segs:
            s1, s2 = seg
            assert collinear(s1, pt, s2)
