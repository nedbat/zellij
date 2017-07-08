import itertools
import math

import cairo

from color import random_color, CasaCeramica
from drawing import Drawing
from euclid import Line, Point
from path_tiler import PathTiler
from path_tiler import combine_paths, replay_path, path_in_box

SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)

DWGW = 800
TILEW = int(DWGW/5)
LINE_WIDTH = TILEW/12

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
        dwg.move_to(*side_top)
        dwg.line_to(*side_bottom)

        shoulder_top = shoulder_line.intersect(shoulder_limit)
        shoulder_bottom = shoulder_line.intersect(snip_line)
        dwg.move_to(*shoulder_top)
        dwg.line_to(*shoulder_bottom)

        foot_top = foot_line.intersect(snip_line)
        foot_bottom = foot_line.intersect(border_side)
        dwg.move_to(*foot_top)
        dwg.line_to(*foot_bottom)

        dwg.move_to(*snip_top)
        dwg.line_to(*foot_top)
        dwg.move_to(*shoulder_bottom)
        dwg.line_to(*snip_bottom)

    def draw_triangle(self):
        self.three_points()
        dwg.move_to(*self.top)
        dwg.line_to(*self.bottom)
        dwg.line_to(*self.belly)
        dwg.close_path()


dwg = Drawing(DWGW, DWGW, bg=(.85, .85, .85))
pt = PathTiler()
draw = Draw(TILEW)

if 1:
    pt.tile_p6m(draw.draw_tile, dwg.get_size(), TILEW)
else:   # Draw one triangle
    pt.translate(400, 400)
    pt.scale(2, 2)
    draw_tile(pt, args=(TILEW,))

if 1:
    paths = combine_paths(pt.paths)
else:
    paths = pt.paths


dwg.set_line_cap(cairo.LineCap.ROUND)
dwg.multi_stroke(paths, [
    #(5, random_color),
    (LINE_WIDTH, (0, 0, 0)),
    (LINE_WIDTH*.7, (1, 1, 1)),
])


if 1:
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

dwg.write_to_png('three_stars.png')
