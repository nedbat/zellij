"""
Simple 2D Euclidean geometric primitives.
"""

from collections import namedtuple
import math


def isclose(a, b):
    return math.isclose(a, b, abs_tol=1e-8)


class BadGeometry(Exception):
    """Any exception raised by euclid."""
    pass


class Point(namedtuple("Point", ["x", "y"])):
    """A point in 2D."""

    def __repr__(self):
        return f"<{self.x:.1f}, {self.y:.1f}>"

    def fullrepr(self):
        return  f"<{self.x}, {self.y}>"

    def is_close(self, other):
        """Are two points close enough to be considered the same?"""
        assert isinstance(other, Point)
        x1, y1 = self
        x2, y2 = other
        return isclose(x1, x2) and isclose(y1, y2)

    def distance(self, other):
        """Compute the distance from this Point to another Point."""
        assert isinstance(other, Point)
        x1, y1 = self
        x2, y2 = other
        return math.hypot(x2 - x1, y2 - y1)

    def in_box(self, ll, ur):
        """Is this point in the box defined by the lower-left and upper-right points?"""
        x, y = self
        llx, lly = ll
        urx, ury = ur
        return (llx <= x <= urx) and (lly <= y <= ury)


def collinear(p1, p2, p3):
    """Do three points lie on a line?"""
    # https://stackoverflow.com/questions/3813681/checking-to-see-if-3-points-are-on-the-same-line
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
    return math.isclose((y1 - y2) * (x1 - x3), (y1 - y3) * (x1 - x2), abs_tol=1e-6)


def along_the_way(p1, p2, t):
    """Return the point t-fraction along the line from p1 to p2"""
    return Point(p1.x + (p2.x - p1.x) * t, p1.y + (p2.y - p1.y) * t)


class Line(namedtuple("Line", ["p1", "p2"])):
    """A line in 2D, defined by two Points."""

    def intersect(self, other):
        """
        Find the point where this Line and another intersect.

        Raises BadGeometry if the lines are parallel or coincident.
        """
        # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        assert isinstance(other, Line)
        (x1, y1), (x2, y2) = self
        (x3, y3), (x4, y4) = other

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if isclose(denom, 0):
            raise BadGeometry("Lines don't intersect usefully: denom = {}".format(denom))

        a = x1 * y2 - y1 * x2
        b = x3 * y4 - y3 * x4

        xi = (a * (x3 - x4) - b * (x1 - x2)) / denom
        yi = (a * (y3 - y4) - b * (y1 - y2)) / denom

        return Point(xi, yi)

    def offset(self, distance):
        """Create another Line `distance` from this one."""
        (x1, y1), (x2, y2) = self
        dx = x2 - x1
        dy = y2 - y1
        hyp = math.hypot(dx, dy)
        offx = dy / hyp * distance
        offy = -dx / hyp * distance
        return Line(Point(x1 + offx, y1 + offy), Point(x2 + offx, y2 + offy))
