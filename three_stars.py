import collections
import itertools
import math
import pprint

import cairo

from color import random_color, CasaCeramica
from drawing import Drawing
from euclid import Line, Point
from path_tiler import PathTiler
from path_tiler import combine_paths, replay_path, path_in_box, offset_path, paths_box

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
    with dwg.line_style(rgb=(1, 0, 0), width=2, dash=[5, 5]):
        pt.replay_paths(dwg)
        dwg.stroke()

    pt = PathTiler()
    pt.translate(2 * TILEW * SQRT3 / 2, TILEW)
    pt.reflect_xy(0, 0)
    draw.draw_tile(pt, ())
    with dwg.line_style(rgb=(0, 0, 0), width=6):
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


if 0:
    TILEW = int(DWGW/5)
    dwg = Drawing(DWGW, DWGW)
    draw_it(TILEW, dwg, fat=False, offset=5, color=(.7,.7,.7))
    draw_it(TILEW, dwg, fat=False, offset=-5, color=(.7,.7,.7))
    #draw_it(TILEW, dwg, fat=False, offset=2.5, color=(.5,.5,.5))
    #draw_it(TILEW, dwg, fat=False, offset=-2.5, color=(.5,.5,.5))
    draw_it(TILEW, dwg, fat=False)
    dwg.write_to_png('three_stars_offset.png')


def debug_output(dwgw=None, paths=None, segments=None, isects=None):
    ll, ur = paths_box(paths)
    dx, dy = int(ur.x - ll.x), int(ur.y - ll.y)
    dwgdbg = Drawing(dx, dy)
    dwgdbg.translate(-ll.x, -ll.y)
    with dwgdbg.line_style(rgb=(0, 0, 0), width=1):
        for (x1, y1), (x2, y2) in segments:
            dwgdbg.move_to(x1, y1)
            dwgdbg.line_to(x2, y2)
            dwgdbg.stroke()

    dup_segments = []
    segments.sort()
    for s1, s2 in zip(segments, segments[1:]):
        if s1 == s2:
            dup_segments.append(s1)

    with dwgdbg.line_style(rgb=(1, 0, 0), width=7):
        for (x1, y1), (x2, y2) in dup_segments:
            dwgdbg.move_to(x1, y1)
            dwgdbg.line_to(x2, y2)
            dwgdbg.stroke()

    if dwgw is not None:
        with dwgdbg.line_style(rgb=(0, 0, 1), width=2, dash=[5, 5]):
            dwgdbg.rectangle(0, 0, dwgw, dwgw)
            dwgdbg.stroke()

    if isects is not None:
        with dwgdbg.line_style(rgb=(0, 1, 0), width=2):
            for pt in isects:
                dwgdbg.circle(pt[0], pt[1], 5)
                dwgdbg.stroke()

    dwgdbg.write_to_png("debug.png")


if 1:
    import poly_point_isect

    TILEW = int(DWGW/2)
    dwg = Drawing(DWGW, DWGW)
    pt = PathTiler()
    pt.rotate(5)
    draw = Draw(TILEW)
    pt.tile_p6m(draw.draw_tile, dwg.get_size(), TILEW)
    paths = pt.paths
    paths = combine_paths(pt.paths)

    segments = []
    segs_to_paths = {}
    for path in paths:
        for p1, p2 in zip(path, path[1:]):
            segment = (tuple(p1), tuple(p2))
            segments.append(segment)
            segs_to_paths[tuple(sorted(segment))] = path

    isects = poly_point_isect.isect_segments_include_segments(segments)
    isect_points = [isect[0] for isect in isects]

    paths_to_intersections = collections.defaultdict(list)

    for isect, segs in isects:
        for seg in segs:
            paths_to_intersections[tuple(segs_to_paths[tuple(sorted(seg))])].append((seg, isect))

    pprint.pprint(paths_to_intersections)

    debug_output(dwgw=DWGW, paths=paths, segments=segments, isects=isect_points)
