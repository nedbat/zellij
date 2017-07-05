import math

import cairo

from drawing import Drawing, random_color
from euclid import Line, Point
from path_tiler import PathTiler
from path_tiler import combine_paths


DWGW = 800
TILEW = int(DWGW/5)
OFFSET = 20
LINE_WIDTH = TILEW/10

def draw_tile(dwg):
    top = Point(0, 0)
    bottom = Point(0, -TILEW)
    belly = (TILEW * math.sqrt(3) / 4, -TILEW*.75)
    border_side = Line(top, bottom)
    border_shoulder = Line(top, belly)
    border_foot = Line(belly, bottom)

    side_line = border_side.offset(-OFFSET)
    side_top = side_line.intersect(border_shoulder)
    side_bottom = side_line.intersect(border_foot)
    dwg.move_to(*side_top)
    dwg.line_to(*side_bottom)

    shoulder_line = border_shoulder.offset(OFFSET)
    shoulder_top = shoulder_line.intersect(border_side)
    shoulder_bottom = shoulder_line.intersect(border_foot)
    dwg.move_to(*shoulder_top)
    dwg.line_to(*shoulder_bottom)

    foot_line = border_foot.offset(OFFSET)
    foot_top = foot_line.intersect(border_shoulder)
    foot_bottom = foot_line.intersect(border_side)
    dwg.move_to(*foot_top)
    dwg.line_to(*foot_bottom)

dwg = Drawing(DWGW, DWGW)
pt = PathTiler()

pt.tile_p6m(draw_tile, dwg.get_size(), TILEW)
paths = combine_paths(pt.paths)

dwg.set_line_cap(cairo.LineCap.ROUND)
dwg.multi_stroke(paths, [
    (LINE_WIDTH, random_color),
    (5, (1, 1, 1)),
])
dwg.write_to_png('three_stars.png')
