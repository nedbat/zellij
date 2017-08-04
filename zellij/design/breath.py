from zellij.design.base import PmmDesign
from zellij.euclid import Line, Point

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
