import collections
import itertools
import math
import pprint

import cairo

from zellij.color import random_color, CasaCeramica
from zellij.drawing import Drawing, DrawingSequence
from zellij.euclid import Line, Point, Segment
from zellij.path_tiler import PathTiler
from zellij.path_tiler import (
    combine_paths, replay_path, path_in_box, offset_path,
    path_segments, join_paths, show_path, trim_path,
)

SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)


class Draw:
    def __init__(self, tilew):
        self.tilew = tilew

    def three_points(self):
        self.top = Point(0, 0)
        self.bottom = Point(0, -self.tilew)
        self.belly = Point(self.tilew * SQRT3 / 4, -self.tilew * .75)

    def draw_tile(self, dwg, args):
        self.three_points()
        border_side = Line(self.top, self.bottom)
        border_shoulder = Line(self.top, self.belly)
        border_foot = Line(self.belly, self.bottom)

        offset = self.tilew/8
        side_line = border_side.offset(-offset)
        shoulder_line = border_shoulder.offset(offset)
        foot_line = border_foot.offset(offset)

        with dwg.saved():
            dwg.translate(*self.belly)
            dwg.rotate(30)
            snip_top = dwg.in_device(0, offset * SQRT2)
            snip_bottom = dwg.in_device(-offset * SQRT2, 0)

        snip_top = dwg.in_user(*snip_top)
        snip_bottom = dwg.in_user(*snip_bottom)
        snip_line = Line(snip_top, snip_bottom)

        far_left = Point(-self.tilew * SQRT3 / 2, -self.tilew / 2)
        shoulder_limit = Line(far_left, self.top)
        shoulder_limit = shoulder_limit.offset(offset)

        far_right = Point(self.tilew * SQRT3 / 2, 0)
        side_limit = Line(self.top, far_right)
        side_limit = side_limit.offset(offset)

        side_top = side_line.intersect(side_limit)
        side_bottom = side_line.intersect(border_foot)
        shoulder_top = shoulder_line.intersect(shoulder_limit)
        shoulder_bottom = shoulder_line.intersect(snip_line)
        foot_top = foot_line.intersect(snip_line)
        foot_bottom = foot_line.intersect(border_side)

        dwg.move_to(*side_top)
        dwg.line_to(*side_bottom)

        dwg.move_to(*shoulder_top)
        dwg.line_to(*shoulder_bottom)
        dwg.line_to(*snip_bottom)

        dwg.move_to(*snip_top)
        dwg.line_to(*foot_top)
        dwg.line_to(*foot_bottom)

    def draw_triangle(self, dwg, args):
        self.three_points()
        dwg.move_to(*self.top)
        dwg.line_to(*self.bottom)
        dwg.line_to(*self.belly)
        dwg.close_path()


def draw_it(TILEW, dwg, combined=True, fat=True, color=(0, 0, 0), line_width=2, offset=None):
    pt = PathTiler()
    draw = Draw(TILEW)
    pt.tile_p6m(draw.draw_tile, dwg.get_size(), TILEW)
    paths = pt.paths
    if combined:
        paths = combine_paths(pt.paths)
    if offset is not None:
        paths = [offset_path(p, offset) for p in paths]
    dwg.set_line_cap(cairo.LineCap.ROUND)

    if fat:
        LINE_WIDTH = TILEW / 12
        styles = [
            (LINE_WIDTH, (0, 0, 0)),
            (LINE_WIDTH*.7, (1, 1, 1)),
        ]
    else:
        styles = [(line_width, color)]
    dwg.multi_stroke(paths, styles)


if 0:
    paths_in_box = [path for path in paths if path_in_box(path, (0, 0), (DWGW, DWGW))]
    drawn = set()
    colors = iter(itertools.cycle([
        CasaCeramica.DarkGreen,
        CasaCeramica.Yellow,
        CasaCeramica.Red,
        CasaCeramica.NavyBlue,
    ]))
    for path in paths_in_box:
        if len(path) not in drawn:
            dwg.set_source_rgb(*next(colors))
            dwg.set_line_width(LINE_WIDTH*.7)
            replay_path(path, dwg)
            dwg.stroke()
            drawn.add(len(path))

DWGW = 800

def talk_pictures():
    TILEW = int(DWGW/3)

    dwg = Drawing(DWGW, DWGW, bg=(.85, .85, .85))
    draw_it(TILEW, dwg)
    dwg.write_to_png('three_stars_0.png')


    dwg = Drawing(DWGW, DWGW)
    draw_it(TILEW, dwg, fat=False)
    dwg.write_to_png('three_stars_1_thin.png')


    dwg = Drawing(DWGW, DWGW)
    draw_it(TILEW, dwg, fat=False, color=(.8, .8, .8))

    pt = PathTiler()
    draw = Draw(TILEW)
    pt.tile_p6m(draw.draw_triangle, dwg.get_size(), TILEW)
    with dwg.style(rgb=(1, 0, 0), width=2, dash=[5, 5]):
        pt.replay_paths(dwg)
        dwg.stroke()

    pt = PathTiler()
    pt.translate(2 * TILEW * SQRT3 / 2, TILEW)
    pt.reflect_xy(0, 0)
    draw.draw_tile(pt, ())
    with dwg.style(rgb=(0, 0, 0), width=6):
        pt.replay_paths(dwg)
        dwg.stroke()

    dwg.write_to_png('three_stars_2_lined.png')


    dwg = Drawing(DWGW, DWGW)
    draw_it(TILEW, dwg, fat=False, color=random_color, combined=False, line_width=8)
    dwg.write_to_png('three_stars_3_chaos.png')


    dwg = Drawing(DWGW, DWGW)
    draw_it(TILEW, dwg, fat=False, color=random_color, combined=True, line_width=8)
    dwg.write_to_png('three_stars_4_joined.png')

#talk_pictures()

def final():
    TILEW = int(DWGW/5)

    dwg = Drawing(DWGW, DWGW, bg=(.85, .85, .85))
    draw_it(TILEW, dwg)
    dwg.write_to_png('three_stars_final.png')

#final()


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

if 1:
    import poly_point_isect

    TILEW = int(DWGW/1)
    dwg = Drawing(DWGW, DWGW)
    pt = PathTiler()
    pt.rotate(2)
    draw = Draw(TILEW)
    pt.tile_p6m(draw.draw_tile, dwg.get_size(), TILEW)
    paths = pt.paths
    paths = combine_paths(pt.paths)
    paths = [tuple(path) for path in paths]

    segments = []
    segs_to_paths = {}
    for path in paths:
        for segment in path_segments(path):
            segments.append(segment)
            segs_to_paths[segment] = path

    isects = poly_point_isect.isect_segments_include_segments(segments)
    points_to_segments = dict(isects)
    isect_points = [isect[0] for isect in isects]

    segs_to_points = collections.defaultdict(list)
    for pt, segs in points_to_segments.items():
        for seg in segs:
            segs_to_points[seg].append(pt)

    points_to_paths = collections.defaultdict(list)
    for isect, segs in isects:
        for seg in segs:
            points_to_paths[isect].append(segs_to_paths[seg])

    print(f"{len(isect_points)} intersections")

    debug_output(dwgw=DWGW, paths=paths, segments=segments, isects=isect_points)

    if 0:
        dwg = Drawing(paths=paths)
        with dwg.style(rgb=(0, 0, 0), width=1):
            for path in paths:
                for piece in path_pieces(path, segs_to_points):
                    replay_path(piece, dwg, gap=.1)
                    dwg.stroke()
        dwg.write_to_png("gap.png")

    class Xing:
        def __init__(self, under=None, over=None):
            self.under = under
            self.over = over
            self.over_piece = None

        def __repr__(self):
            return f"<Xing under={show_path(self.under)} over={show_path(self.over)}>"

    STRAP_WIDTH = 20
    class Strap:
        def __init__(self, path):
            self.path = path
            self.sides = [offset_path(path, d) for d in [STRAP_WIDTH/2, -STRAP_WIDTH/2]]

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

    if 1:
        dbgdwgs = iter(DrawingSequence(name="debugs_.png", paths=paths))
    else:
        dbgdwgs = None

    paths_to_do = set(paths)
    paths_done = set()
    xings = {}      # pt -> xing
    straps = []     # new smaller paths, ending at unders.
    path = None
    while paths_to_do:
        next_paths = set()
        skips = [paths_to_do.pop() for _ in range(1)]
        next_paths.add(paths_to_do.pop())
        paths_to_do.update(skips)
        while next_paths:
            previous_path = path
            path = next_paths.pop()

            if dbgdwgs:
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
                if first_piece and dbgdwgs:
                    dwg.cross_points([piece[0], piece[-1]], radius=20, rgb=(1, 0, 0), width=5)
                    dwg.write()
                    if dwg.num > 10:
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
                        strap = Strap(join_paths(prev_piece, piece))
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
                        straps.append(Strap(piece))
                    last_cut = piece[-1]
                    prev_piece = None
                if cut:
                    for next_path in points_to_paths[cut]:
                        if next_path in paths_to_do:
                            paths_to_do.remove(next_path)
                            next_paths.add(next_path)
            if prev_piece:
                strap = Strap(prev_piece)
                straps.append(strap)

            paths_done.add(path)

            if dbgdwgs:
                dwg.cross_points([piece[0], piece[-1]], radius=20, rotate=45, rgb=(0, 0, 1), width=5)
                dwg.write()
                if dwg.num > 10:
                    print()
                    import sys; sys.exit()

    bad = [pt for pt, xing in xings.items() if xing.over_piece is None]
    debug_output(dwgw=DWGW, paths=paths, segments=segments, isects=bad)

    for strap in straps:
        sides = strap.sides
        for end in [0, -1]:
            xing = xings.get(strap.path[end])
            if xing is not None:
                trimmers = xing.over_piece.sides
                strap.sides = [trim_path(s, end, trimmers) for s in strap.sides]

    if 1:
        colors = [
            CasaCeramica.DarkGreen,
            CasaCeramica.Yellow,
            CasaCeramica.Red,
            CasaCeramica.NavyBlue,
        ]
        dwg = Drawing(paths=paths, name="straps.png")#DWGW, DWGW)  #(paths=paths)
        if 0:
            with dwg.style(rgb=(0, 0, 0), width=1):
                for path in paths:
                    replay_path(path, dwg)
                    dwg.stroke()
        with dwg.style(rgb=(0, 0, 0), width=1):
            for strap in straps:
                if 0:
                    with dwg.style(rgb=colors[len(strap.path) % len(colors)]):
                        replay_path(strap.sides[0], dwg)
                        replay_path(strap.sides[1][::-1], dwg, start=False)
                        dwg.close_path()
                        dwg.fill()

                for side in strap.sides:
                    replay_path(side, dwg)
                    dwg.stroke()

        dwg.write()
