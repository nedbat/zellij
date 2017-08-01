"""Strappiness for Zellij."""

import collections
import itertools
import random

from zellij.euclid import Point, Segment
from zellij.intersection import segment_intersections
from zellij.path_tiler import join_paths, offset_path, path_segments, trim_path


class Xing:
    def __init__(self, under=None, over=None):
        self.under = under
        self.over = over
        self.over_piece = None

    def __repr__(self):
        return f"<Xing under={show_path(self.under)} over={show_path(self.over)}>"

class Strap:
    def __init__(self, path, width, random_factor=0):
        self.path = path
        if random_factor:
            width *= (1 + random.random() * random_factor)
        self.sides = [offset_path(path, d) for d in [width/2, -width/2]]


def path_pieces(path, segs_to_points):
    """Produce a new series of paths, split at intersection points.

    Yields a series of pieces (paths).  The pieces trace the same line as the
    original path.  The endpoints of the pieces are all intersection points
    in `segs_to_points`, or the endpoints of the original path, if it isn't
    circular.  The pieces are in order along `path`, so consecutive pieces
    end and begin at the same point. If `path` is closed, then the first piece
    returned will begin at the first cut, not at the path's first point.

    """
    # If path is circular, then the first piece we collect has to be added to
    # the last piece, so save it for later.
    collecting_head = (path[0] == path[-1])
    head = None

    piece = []
    for pt in path:
        if not piece:
            piece.append(pt)
        else:
            seg = Segment(piece[-1], pt)
            cuts = segs_to_points.get(seg)
            if cuts is not None:
                cuts = seg.sort_along(cuts)
                for cut in cuts:
                    ptcut = Point(*cut)
                    piece.append(ptcut)
                    if collecting_head:
                        head = piece
                        collecting_head = False
                    else:
                        yield piece
                    piece = [ptcut]
            piece.append(pt)

    if head:
        piece = join_paths(piece, head)
    yield piece


def strapify(paths, **strap_kwargs):
    """Turn paths intro straps."""

    ###- paths

    segments = []
    segs_to_paths = {}
    for path in paths:
        for segment in path_segments(path):
            segments.append(segment)
            segs_to_paths[segment] = path

    points_to_segments = segment_intersections(segments)
    isect_points = list(points_to_segments.keys())

    segs_to_points = collections.defaultdict(list)
    for pt, segs in points_to_segments.items():
        for seg in segs:
            segs_to_points[seg].append(pt)

    points_to_paths = collections.defaultdict(list)
    for isect, segs in points_to_segments.items():
        for seg in segs:
            points_to_paths[isect].append(segs_to_paths[seg])

    ###- paths, segs_to_points, points_to_paths

    print(f"{len(isect_points)} intersections")

    if 0:
        debug_output(dwgw=DWGW, paths=paths, segments=segments, isects=isect_points)

    def pieces_under_over(path, segs_to_points, xings):
        """Produce all the pieces of the path, with a bool indicating if each leads to under or over."""
        pieces = list(path_pieces(path, segs_to_points))
        for i, piece in enumerate(pieces):
            xing = xings.get(piece[-1])
            if xing is None:
                continue
            if xing.under == path:
                over = False
            elif xing.over == path:
                over = True
            elif xing.under is not None:
                over = True
            else:
                assert xing.over is not None
                over = False
            ou = [over, not over]
            if i % 2:
                ou = ou[::-1]
            break
        else:
            ou = [True, False]

        yield from zip(pieces, itertools.cycle(ou))

    paths_to_do = set(paths)
    xings = {}      # pt -> xing
    straps = []     # new smaller paths, ending at unders.
    path = None
    while paths_to_do:
        next_paths = set()
        next_paths.add(paths_to_do.pop())
        while next_paths:
            path = next_paths.pop()

            prev_piece = None
            last_cut = None
            for piece, over in pieces_under_over(path, segs_to_points, xings):
                cut = None
                if over:
                    assert prev_piece is None
                    prev_piece = piece
                    if last_cut:
                        cut = last_cut
                        xing = xings.get(cut)
                        if xing is None:
                            xing = Xing(under=path)
                            xings[cut] = xing
                        else:
                            assert xing.under is None or xing.under == path
                            xing.under = path
                        last_cut = None
                else:
                    if prev_piece:
                        cut = prev_piece[-1]
                        assert cut == piece[0]
                        strap = Strap(join_paths(prev_piece, piece), **strap_kwargs)
                        straps.append(strap)
                        xing = xings.get(cut)
                        if xing is None:
                            xing = Xing(over=path)
                            xings[cut] = xing
                        else:
                            assert xing.over is None or xing.over == path
                            xing.over = path
                        xing.over_piece = strap
                    else:
                        straps.append(Strap(piece, **strap_kwargs))
                    last_cut = piece[-1]
                    prev_piece = None
                if cut:
                    for next_path in points_to_paths[cut]:
                        if next_path in paths_to_do:
                            paths_to_do.remove(next_path)
                            next_paths.add(next_path)
            if prev_piece:
                strap = Strap(prev_piece, **strap_kwargs)
                straps.append(strap)
                closed = (path[0] == path[-1])
                if closed:
                    cut = prev_piece[-1]
                    xing = xings.get(cut)
                    if xing is None:
                        xing = Xing(over=path)
                        xings[cut] = xing
                    else:
                        xing.over = path
                    xing.over_piece = strap

    if 0:
        bad = [pt for pt, xing in xings.items() if xing.over_piece is None]
        debug_output(dwgw=DWGW, paths=paths, segments=segments, isects=bad)

    ###- straps, xings

    for strap in straps:
        sides = strap.sides
        for end in [0, -1]:
            xing = xings.get(strap.path[end])
            if xing is not None:
                trimmers = xing.over_piece.sides
                strap.sides = [trim_path(s, end, trimmers) for s in strap.sides]

    ###- straps

    return straps


def debug_output(dwgw=None, paths=None, segments=None, isects=None):
    dwg = Drawing(paths=paths, name="debug.png")
    dwg.draw_segments(segments, rgb=(0, 0, 0), width=1)

    dup_segments = []
    segments.sort()
    for s1, s2 in zip(segments, segments[1:]):
        if s1 == s2:
            dup_segments.append(s1)

    dwg.draw_segments(dup_segments, rgb=(1, 0, 0), width=7)

    if dwgw is not None:
        with dwg.style(rgb=(0, 0, 1), width=2, dash=[5, 5]):
            dwg.rectangle(0, 0, dwgw, dwgw)
            dwg.stroke()

    if isects is not None:
        dwg.circle_points(isects, radius=9, rgb=(0, .5, 0), width=3)

    dwg.write()
