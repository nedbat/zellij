"""Wrapper around poly_point_isect."""

import affine
import poly_point_isect

from .defuzz import Defuzzer
from .euclid import Segment


class IntersectionFailure(Exception):
    pass


def segment_intersections(segments):
    """Returns a dict mapping points to lists of segments."""
    defuzz = Defuzzer().defuzz
    for s in segments:
        defuzz(s[0])
        defuzz(s[1])

    # poly_point_isect can fail with AssertionErrors.  Rotating all the
    # segments avoids them, but different angles work for different sets of
    # segments.  Try a few until we succeed.  This is super-lame...
    for angle in [x/6 for x in range(0, 6*10)]:
        rot = affine.Affine.rotation(angle)
        rotsegs = [(rot * s[0], rot * s[1]) for s in segments]
        try:
            pt_segments = poly_point_isect.isect_segments_include_segments(rotsegs)
        except AssertionError:
            continue

        rot = affine.Affine.rotation(-angle)
        intersections = {}
        for pt, segs in pt_segments:
            rotsegs = [Segment(defuzz(rot * s[0]), defuzz(rot * s[1])) for s in segs]
            intersections[rot * pt] = rotsegs

        return intersections

    raise IntersectionFailure()
