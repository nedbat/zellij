"""Wrapper around poly_point_isect."""

import affine
import poly_point_isect

from .defuzz import Defuzzer
from .euclid import Segment


def segment_intersections(segments):
    """Returns a dict mapping points to lists of segments."""
    dfz = Defuzzer()
    for s in segments:
        dfz.defuzz(s[0])
        dfz.defuzz(s[1])

    rot = affine.Affine.rotation(2)
    rotsegs = [(rot * s[0], rot * s[1]) for s in segments]
    pt_segments = poly_point_isect.isect_segments_include_segments(rotsegs)

    rot = affine.Affine.rotation(-2)
    intersections = {}
    for pt, segs in pt_segments:
        rotsegs = [Segment(dfz.defuzz(rot * s[0]), dfz.defuzz(rot * s[1])) for s in segs]
        intersections[rot * pt] = rotsegs

    return intersections
