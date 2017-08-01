"""Zellij-specific helpers for Hypothesis."""

from hypothesis.strategies import builds, floats, integers, one_of

from zellij.euclid import Point

LIMIT = 10000

# Numbers that are reasonable for Zellij.
f = floats(min_value=-LIMIT, max_value=LIMIT)
i = integers(min_value=-LIMIT, max_value=LIMIT)

# Points, on an integer grid to avoid some hairiness with pathological floats.
ipoints = builds(Point, i, i)
fpoints = builds(Point, f, f)

# A parameter for positioning along a line segment, including beyond the
# endpoints.
t_zero_one = one_of(
    # Make half the values be in -1..2:
    builds(lambda i: i/1000, integers(min_value=-1000, max_value=2000)),
    # The other half can be wider-ranging:
    builds(lambda i: i/1000, integers(min_value=-100000, max_value=100000)),
)
