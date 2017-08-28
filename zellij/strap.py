"""Strappiness for Zellij."""

import collections
import itertools
import random

from zellij.debug import should_debug
from zellij.drawing import DrawingSequence
from zellij.euclid import Point, Segment
from zellij.intersection import segment_intersections
from zellij.path import Path, show_path


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
        self.sides = [path.offset_path(d) for d in [width/2, -width/2]]

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
    collecting_head = path.closed
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
                        yield Path(piece)
                    piece = [ptcut]
            piece.append(pt)

    piece = Path(piece)
    if head:
        piece = piece.join(Path(head))
    yield piece


def pieces_under_over(path, segs_to_points, xings):
    """Produce all the pieces of the path, with a bool indicating if each leads to under or over."""
    pieces = list(path_pieces(path, segs_to_points))
    for i, piece in enumerate(pieces):
        xing = xings.get(piece[-1])
        if xing is None:
            continue
        if xing.under is not None:
            over = (xing.under != path)
        else:
            assert xing.over is not None
            over = (xing.over == path)
        ou = [over, not over]
        if i % 2:
            ou = ou[::-1]
        break
    else:
        ou = [True, False]

    yield from zip(pieces, itertools.cycle(ou))


def set_xing(xings, pt, under=None, over=None):
    xing = xings.get(pt)
    if xing is None:
        xing = Xing(under=under, over=over)
        xings[pt] = xing
    elif under is not None:
        assert xing.under is None or xing.under == under
        xing.under = under
    else:
        assert over is not None
        assert xing.over is None or xing.over == over
        xing.over = over
    return xing


def strapify(paths, **strap_kwargs):
    """Turn paths intro straps."""

    segments = []
    segs_to_paths = {}
    for path in paths:
        for segment in path.segments():
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
            closed = (path[0] == path[-1])

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

            # This code works, but is still too convoluted. pieces_under_over
            # generates a whole sequence of pieces and under/over bools, but we
            # really only use the first under/over.  And we don't need to
            # process the pieces in order.  We could combine pieces_under_over,
            # and this loop here, to deal with the straps in a less complicated
            # way.

            cuts = []

            # Get the pieces of the path, and rearrange them.
            piece_overs = list(pieces_under_over(path, segs_to_points, xings))
            if closed:
                cuts.extend(piece_over[0][0] for piece_over in piece_overs)
                if not piece_overs[0][1]:
                    # It starts over, heading to under. Rotate by one.
                    piece_overs = piece_overs[1:] + piece_overs[:1]
                strap_pieces = [(piece_overs[i][0], piece_overs[i+1][0]) for i in range(0, len(piece_overs), 2)]
                # Now strap_pieces is a list of pairs, pieces that make
                # under-over-under straps.
            else:
                cuts.extend(piece_over[0][0] for piece_over in piece_overs[1:])
                strap_pieces = []
                if not piece_overs[0][1]:
                    # First piece heads to under. Reverse it, and add it as a
                    # single-piece strap.
                    strap_pieces.append((piece_overs[0][0].reversed(),))
                    piece_overs = piece_overs[1:]
                strap_pieces.extend([(piece_overs[i][0], piece_overs[i+1][0]) for i in range(0, len(piece_overs)//2*2, 2)])
                if len(piece_overs) % 2:
                    # There's a piece left. It must head to an over. Add it as
                    # a single-piece strap.
                    strap_pieces.append((piece_overs[-1][0],))

            for strap_piece in strap_pieces:
                set_xing(xings, strap_piece[0][0], under=path)
                over_xing = set_xing(xings, strap_piece[0][-1], over=path)
                if len(strap_piece) == 2:
                    # An under-over-under strap
                    strap = Strap(strap_piece[0].join(strap_piece[1]), **strap_kwargs)
                    set_xing(xings, strap_piece[1][-1], under=path)
                else:
                    # An under-to-over strap
                    strap = Strap(strap_piece[0], **strap_kwargs)
                over_xing.over_piece = strap
                straps.append(strap)

            for cut in cuts:
                for next_path in points_to_paths[cut]:
                    if next_path in paths_to_do:
                        paths_to_do.remove(next_path)
                        next_paths.add(next_path)

            paths_done.add(path)
            if debug:
                dwg.finish()
                if 0 and dwg.num > 10:
                    print()
                    import sys; sys.exit()

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
            if xing is not None and xing.over_piece is not None and xing.over_piece is not strap:
                trimmers = xing.over_piece.sides
                strap.sides = [s.trim(end, trimmers) for s in strap.sides]

    return straps
