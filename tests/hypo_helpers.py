"""Zellij-specific helpers for Hypothesis."""

from hypothesis.strategies import builds, floats, integers, tuples

from zellij.euclid import Point

LIMIT = 10000

# Numbers that are reasonable for Zellij.
f = floats(min_value=-LIMIT, max_value=LIMIT, allow_nan=False, allow_infinity=False)
i = integers(min_value=-LIMIT, max_value=LIMIT)

# Points, on an integer grid to avoid some hairiness with pathological floats.
points = builds(Point, i, i)

# A parameter for positioning along a line segment, including beyond the
# endpoints.
t_zero_one = floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False).filter(lambda f: abs(f) > 1e-4)
