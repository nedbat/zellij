from zellij.color import random_color
from zellij.drawing import Drawing
from zellij.euclid import Line, Point
from zellij.path_tiler import PathTiler
from zellij.path_tiler import combine_paths

import cairo


DWGW = 800
TILEW = int(DWGW/5)
LINE_WIDTH = TILEW/4

def draw_tile(dwg, args):
    TILEW, = args
    t2 = TILEW/2
    west = Point(0, t2)
    south = Point(t2, 0)
    sqw = west.distance(south)
    southwest = Point(t2-sqw/2, t2-sqw/2)
    diagonal = Line(west, south)
    vert = Line(Point(t2-sqw/2, 0), southwest)
    horz = Line(southwest, Point(0, t2-sqw/2))

    wsw = diagonal.intersect(vert)
    ssw = diagonal.intersect(horz)

    dwg.move_to(*west)
    dwg.line_to(*wsw)
    dwg.line_to(*southwest)
    dwg.line_to(*ssw)
    dwg.line_to(*south)

dwg = Drawing(DWGW, DWGW)
pt = PathTiler()

pt.tile_pmm(draw_tile, dwg.get_size(), TILEW//2, TILEW//2, args=(TILEW,))

paths = combine_paths(pt.paths)

dwg.set_line_cap(cairo.LineCap.ROUND)
dwg.multi_stroke(paths, [
    #(LINE_WIDTH, (0, 0, 0)),
    (LINE_WIDTH-2, random_color),
    #(7, (0, 0, 0)),
    (5, (1, 1, 1)),
])
dwg.write_to_png('breathing.png')
