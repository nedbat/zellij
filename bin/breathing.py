import cairo

from zellij.color import random_color
from zellij.design.base import PmmDesign
from zellij.drawing import Drawing
from zellij.euclid import Line, Point
from zellij.path_tiler import PathTiler
from zellij.path_tiler import combine_paths


DWGW = 800
TILEW = int(DWGW/8)
LINE_WIDTH = TILEW/4

class BreathDesign(PmmDesign):
    def draw_tile(self, dwg):
        west = Point(0, self.tilew)
        south = Point(self.tilew, 0)
        sqw = west.distance(south)
        southwest = Point(self.tilew-sqw/2, self.tilew-sqw/2)
        diagonal = Line(west, south)
        vert = Line(Point(self.tilew-sqw/2, 0), southwest)
        horz = Line(southwest, Point(0, self.tilew-sqw/2))

        wsw = diagonal.intersect(vert)
        ssw = diagonal.intersect(horz)

        dwg.move_to(*west)
        dwg.line_to(*wsw)
        dwg.line_to(*southwest)
        dwg.line_to(*ssw)
        dwg.line_to(*south)

dwg = Drawing(DWGW, DWGW)
pt = PathTiler()
draw = BreathDesign(TILEW)
draw.draw(pt, dwg.get_size())

paths = combine_paths(pt.paths)

dwg.set_line_cap(cairo.LineCap.ROUND)
dwg.multi_stroke(paths, [
    #(LINE_WIDTH, (0, 0, 0)),
    (LINE_WIDTH-2, random_color),
    #(7, (0, 0, 0)),
    (5, (1, 1, 1)),
])
dwg.write_to_png('breathing.png')
