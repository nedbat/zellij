"""Zellij-specific helpers for Hypothesis."""

from hypothesis.strategies import builds, floats, tuples

from euclid import Point


# Floats that are reasonable for Zellij.
f = floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False)

# Points.
points = builds(Point, f, f)

# A parameter for positioning along a line segment, including beyond the
# endpoints.
t_zero_one = floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False).filter(lambda f: abs(f) > 1e-4)
