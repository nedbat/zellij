"""Strappiness for Zellij."""

import collections
import itertools
import random

from zellij.debug import should_debug
from zellij.drawing import Drawing, DrawingSequence
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

    def __repr__(self):
        return f"<Strap path={self.path}>"


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


def strapify(paths, **strap_kwargs):
    """Turn paths intro straps."""

    paths = [tuple(path) for path in paths]

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

    print(f"{len(isect_points)} intersections")

    if 0:
        debug_output(dwgw=DWGW, paths=paths, segments=segments, isects=isect_points)

    debug = should_debug("strapify")
    if debug:
        dbgdwgs = iter(DrawingSequence(name="debugs_", paths=paths))

    paths_to_do = set(paths)
    paths_done = set()
    xings = {}      # pt -> xing
    straps = []     # new smaller paths, ending at unders.
    path = None
    while paths_to_do:
        next_paths = set()
        next_paths.add(paths_to_do.pop())
        while next_paths:
            previous_path = path
            path = next_paths.pop()

            if debug:
                dwg = next(dbgdwgs)
                dwg.draw_segments(segments, rgb=(0, 0, 0), width=1)
                dwg.draw_paths(paths_done, rgb=(0, 0, 0), width=3)
                dwg.draw_paths(next_paths, rgb=(.7, .7, 0), width=9)
                if previous_path:
                    dwg.draw_path(previous_path, rgb=(1, 0, 0), width=10, dash=[30, 30])
                dwg.draw_path(path, rgb=(1, 0, 0), width=15)
                dwg.fill_points([path[0]], rgb=(1, 0, 0), radius=15*3/2)
                dwg.fill_points([path[1]], rgb=(1, 0, 0), radius=15*2/2)
                partial_over = [pt for pt, xing in xings.items() if xing.under is None]
                partial_under = [pt for pt, xing in xings.items() if xing.over is None]
                dwg.circle_points(partial_over, rgb=(.8, 0, 0), radius=21, width=9)
                dwg.circle_points(partial_under, rgb=(0, 0, .8), radius=21, width=9)
                done = [pt for pt, xing in xings.items() if xing.under is not None and xing.over is not None]
                dwg.circle_points(done, rgb=(0, .8, 0), radius=15, width=3)

            prev_piece = None
            last_cut = None
            first_piece = True
            for piece, over in pieces_under_over(path, segs_to_points, xings):
                if first_piece and debug:
                    dwg.cross_points([piece[0], piece[-1]], radius=20, rgb=(1, 0, 0), width=5)
                    dwg.finish()
                    if 0 and dwg.num > 10:
                        print()
                        import sys; sys.exit()
                    first_piece = False

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

            paths_done.add(path)
            if debug:
                dwg.cross_points([piece[0], piece[-1]], radius=30, rotate=30, rgb=(0, 0, 1), width=5)
                dwg.finish()
                if 0 and dwg.num > 10:
                    print()
                    import sys; sys.exit()

    if 0:
        bad = [pt for pt, xing in xings.items() if xing.over_piece is None]
        debug_output(dwgw=DWGW, paths=paths, segments=segments, isects=bad)

    if debug:
        for strap in straps:
            dwg = next(dbgdwgs)
            dwg.draw_segments(segments, rgb=(0, 0, 0), width=1)
            dwg.draw_path(strap.path, rgb=(1, 0, 0), width=3)
            for s in strap.sides:
                dwg.draw_path(s, rgb=(0, 0, 1), width=1)
            dwg.finish()

    for strap in straps:
        for end in [0, -1]:
            xing = xings.get(strap.path[end])
            if xing is not None:
                trimmers = xing.over_piece.sides
                strap.sides = [trim_path(s, end, trimmers) for s in strap.sides]

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

    dwg.finish()
