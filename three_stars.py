import itertools
import math

import cairo

from color import random_color, CasaCeramica
from drawing import Drawing
from euclid import Line, Point
from path_tiler import PathTiler
from path_tiler import combine_paths, replay_path, path_in_box


DWGW = 800
TILEW = int(DWGW/5)
LINE_WIDTH = TILEW/12

def draw_tile(dwg, args):
    TILEW, = args
    OFFSET = TILEW/8
    top = Point(0, 0)
    bottom = Point(0, -TILEW)
    belly = (TILEW * math.sqrt(3) / 4, -TILEW*.75)
    border_side = Line(top, bottom)
    border_shoulder = Line(top, belly)
    border_foot = Line(belly, bottom)

    side_line = border_side.offset(-OFFSET)
    shoulder_line = border_shoulder.offset(OFFSET)
    foot_line = border_foot.offset(OFFSET)

    with dwg.saved():
        dwg.translate(*belly)
        dwg.rotate(30)
        snip_top = dwg.in_device(0, OFFSET * math.sqrt(2))
        snip_bottom = dwg.in_device(-OFFSET * math.sqrt(2), 0)

    snip_top = dwg.in_user(*snip_top)
    snip_bottom = dwg.in_user(*snip_bottom)
    snip_line = Line(snip_top, snip_bottom)

    far_left = Point(-TILEW * math.sqrt(3) / 2, -TILEW / 2)
    shoulder_limit = Line(far_left, top)
    shoulder_limit = shoulder_limit.offset(OFFSET)

    far_right = Point(TILEW * math.sqrt(3) / 2, 0)
    side_limit = Line(top, far_right)
    side_limit = side_limit.offset(OFFSET)

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

    if 0:   # Outline the base triangle
        dwg.move_to(*top)
        dwg.line_to(*bottom)
        dwg.line_to(*belly)
        dwg.close_path()

dwg = Drawing(DWGW, DWGW, bg=(.85, .85, .85))
pt = PathTiler()

if 1:
    pt.tile_p6m(draw_tile, dwg.get_size(), TILEW, args=(TILEW,))
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
