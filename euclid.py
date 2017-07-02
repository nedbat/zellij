"""
Simple 2D Euclidean geometric primitives.
"""

from collections import namedtuple
import math


EPSILON = 1e-8

def _near_zero(v):
    return math.isclose(v, 0, abs_tol=EPSILON)


class BadGeometry(Exception):
    """Any exception raised by euclid."""
    pass


class Point(namedtuple("Point", ["x", "y"])):
    """A point in 2D."""

    def __repr__(self):
        return f"<{self.x:.1f}, {self.y:.1f}>"

    def __eq__(self, other):
        assert isinstance(other, Point)
        x1, y1 = self
        x2, y2 = other
        return _near_zero(x1 - x2) and _near_zero(y1 - y2)

    def distance(self, other):
        assert isinstance(other, Point)
        x1, y1 = self
        x2, y2 = other
        return math.hypot(x2 - x1, y2 - y1)


def collinear(p1, p2, p3):
    """Do three points lie on a line?"""
    # https://stackoverflow.com/questions/3813681/checking-to-see-if-3-points-are-on-the-same-line
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
    return _near_zero((y1 - y2) * (x1 - x3) - (y1 - y3) * (x1 - x2))


class Line(namedtuple("Line", ["p1", "p2"])):
    """A line in 2D, defined by two Points."""

    def intersect(self, other):
        """
        Find the point where this line and another intersect.

        Raises BadGeometry if the lines are parallel or coincident.
        """
        # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        assert isinstance(other, Line)
        (x1, y1), (x2, y2) = self
        (x3, y3), (x4, y4) = other

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if _near_zero(denom):
            raise BadGeometry("Lines don't intersect usefully: denom = {}".format(denom))

        a = x1 * y2 - y1 * x2
        b = x3 * y4 - y3 * x4

        xi = (a * (x3 - x4) - b * (x1 - x2)) / denom
        yi = (a * (y3 - y4) - b * (y1 - y2)) / denom

        return Point(xi, yi)
