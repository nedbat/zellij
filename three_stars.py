import math

import cairo

from drawing import Drawing, random_color
from euclid import Line, Point
from path_tiler import PathTiler
from path_tiler import combine_paths


DWGW = 800
TILEW = int(DWGW/5)
OFFSET = 20
LINE_WIDTH = TILEW/30

def draw_tile(dwg):
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
    dwg.move_to(*snip_top)
    dwg.line_to(*snip_bottom)

    side_top = side_line.intersect(border_shoulder)
    side_bottom = side_line.intersect(border_foot)
    dwg.move_to(*side_top)
    dwg.line_to(*side_bottom)

    shoulder_top = shoulder_line.intersect(border_side)
    shoulder_bottom = shoulder_line.intersect(border_foot)
    dwg.move_to(*shoulder_top)
    dwg.line_to(*shoulder_bottom)

    foot_top = foot_line.intersect(border_shoulder)
    foot_bottom = foot_line.intersect(border_side)
    dwg.move_to(*foot_top)
    dwg.line_to(*foot_bottom)

    if 0:   # Outline the base triangle
        dwg.move_to(*top)
        dwg.line_to(*bottom)
        dwg.line_to(*belly)
        dwg.close_path()

dwg = Drawing(DWGW, DWGW)
pt = PathTiler()

if 1:
    pt.tile_p6m(draw_tile, dwg.get_size(), TILEW)
else:   # Draw one triangle
    pt.translate(400,400)
    pt.scale(2, 2)
    draw_tile(pt)
paths = combine_paths(pt.paths)

dwg.set_line_cap(cairo.LineCap.ROUND)
dwg.multi_stroke(paths, [
    (LINE_WIDTH, random_color),
    #(5, (1, 1, 1)),
])
dwg.write_to_png('three_stars.png')
