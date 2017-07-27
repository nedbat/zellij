"""
Simple 2D Euclidean geometric primitives.
"""

from collections import namedtuple
import functools
import math

from .postulates import overlap, fbetween, isclose


class BadGeometry(Exception):
    """Any exception raised by euclid."""
    pass

class ParallelLines(BadGeometry):
    """Two lines considered for intersection are parallel."""
    pass

class CoincidentLines(BadGeometry):
    """Two lines considered for intersection are the same infinite lines."""
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


def line_collinear(x1, y1, x2, y2, x3, y3):
    """Are three points on the same line, regardless of order?"""
    # https://stackoverflow.com/questions/3813681/checking-to-see-if-3-points-are-on-the-same-line
    return isclose((y1 - y2) * (x1 - x3), (y1 - y3) * (x1 - x2))


def collinear(p1, p2, p3):
    """
    Do three points lie on a line?

    The points must be in order: p2 must be between p1 and p3 for this to
    return True.
    """
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
    if fbetween(x1, x2, x3) and fbetween(y1, y2, y3):
        return line_collinear(x1, y1, x2, y2, x3, y3)
    else:
        return False


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
            if line_collinear(x1, y1, x2, y2, x3, y3):
                raise CoincidentLines("No intersection of identical lines")
            else:
                raise ParallelLines("No intersection of parallel lines")

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


def point_cmp(p1, p2):
    """Compare two points, returning -1, 0, or 1.

    $(*&#$%@! float fuzziness is going to be the death of me.
    """
    (x1, y1), (x2, y2) = p1, p2
    if isclose(x1, x2):
        if isclose(y1, y2):
            return 0
        else:
            return 1 if y1 > y2 else -1
    else:
        return 1 if x1 > x2 else -1

point_key = functools.cmp_to_key(point_cmp)

class Segment(namedtuple('Segment', 'p1 p2')):
    def __eq__(self, other):
        return sorted(self) == sorted(other)

    def __hash__(self):
        return hash(tuple(sorted(self)))

    def intersect(self, other):
        """
        Find the point where this Segment and another intersect. Returns None
        if there is no point of intersection, or BadGeometry if the answer is
        undefined.
        """
        l1 = Line(*self)
        l2 = Line(*other)
        try:
            p = l1.intersect(l2)
        except ParallelLines:
            return None
        except CoincidentLines:
            # If the segments overlap, BadGeometry, else, None
            if overlap(self.p1[0], self.p2[0], other.p1[0], other.p2[0]):
                raise CoincidentLines("Segments overlap")
            else:
                return None
        if collinear(self.p1, p, self.p2) and collinear(other.p1, p, other.p2):
            return p
        else:
            return None

    def sort_along(self, points):
        """Sort `points` so that they are ordered from p1 to p2.

        Assumes that `points` lie on the Segment, but makes no check that they
        do.
        """
        return sorted(points, reverse=(point_cmp(self.p1, self.p2) == 1), key=point_key)
