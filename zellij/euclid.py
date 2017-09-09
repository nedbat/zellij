"""
Simple 2D Euclidean geometric primitives.
"""

from collections import namedtuple
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
        return  f"Point({self.x}, {self.y})"

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


def line_collinear(p1, p2, p3):
    """Are three points on the same line, regardless of order?"""
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
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
        return line_collinear(p1, p2, p3)
    else:
        return False


def along_the_way(p1, p2, t):
    """Return the point t-fraction along the line from p1 to p2"""
    return Point(p1.x + (p2.x - p1.x) * t, p1.y + (p2.y - p1.y) * t)


class Line(namedtuple("Line", ["p1", "p2"])):
    """A line in 2D, defined by two Points."""

    def angle(self):
        """The angle in degrees this line makes to the horizontal."""
        (x1, y1), (x2, y2) = self
        return math.degrees(math.atan2(y2 - y1, x2 - x1))

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
            if line_collinear(self.p1, self.p2, other.p1):
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

    def foot(self, point):
        """What point on this line is the perpendicular foot of `point`?"""
        (x1, y1), (x2, y2) = self
        x3, y3 = point

        # https://stackoverflow.com/a/1811636/14343
        k = ((y2-y1) * (x3-x1) - (x2-x1) * (y3-y1)) / ((y2-y1) ** 2 + (x2-x1) ** 2)
        x4 = x3 - k * (y2-y1)
        y4 = y3 + k * (x2-x1)
        return Point(x4, y4)

    def perpendicular(self, thru):
        """Create another Line perpendicular to this one, through `thru`."""
        # We want to return Line(thru, self.foot(thru)), but if thru is on the
        # line, then this is degenerate. Compute a new point off the line.
        (x1, y1), (x2, y2) = self
        dx = x2 - x1
        dy = y2 - y1
        (x3, y3) = foot = self.foot(thru)
        x4 = x3 + dy
        y4 = y3 - dx
        return Line(foot, Point(x4, y4))

    def parallel(self, thru):
        """Create another Line parallel to this one, through `thru`."""
        (x1, y1), (x2, y2) = self
        x3, y3 = thru
        x4 = (x2 - x1) + x3
        y4 = (y2 - y1) + y3
        return Line(thru, Point(x4, y4))


class Segment(namedtuple('Segment', 'p1 p2')):
    """A segment of a line, from p1 to p2."""

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
                raise CoincidentLines("Segments overlap", self, other)
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
        return sorted(points, key=self.p1.distance)


class Bounds(namedtuple('Bounds', 'llx lly urx ury')):
    """A rectangle bounding something in the plane."""

    @classmethod
    def points(cls, pts):
        """The Bounds for a collection of points."""
        return cls(
            min(pt.x for pt in pts),
            min(pt.y for pt in pts),
            max(pt.x for pt in pts),
            max(pt.y for pt in pts),
        )

    @property
    def width(self):
        return self.urx - self.llx

    @property
    def height(self):
        return self.ury - self.lly

    def __or__(self, other):
        return self.__class__(
            min(self.llx, other.llx),
            min(self.lly, other.lly),
            max(self.urx, other.urx),
            max(self.ury, other.ury),
        )

    def expand(self, *, percent):
        """Create a Bounds slightly larger than this one."""
        extra = max(self.width, self.height) * percent / 100
        return Bounds(
            self.llx - extra,
            self.lly - extra,
            self.urx + extra,
            self.ury + extra,
        )
