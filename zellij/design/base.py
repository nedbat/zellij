import math

from zellij.euclid import Point


SQRT3 = math.sqrt(3)

class Design:
    description = None

    def draw(self, dwg):
        pass


class P6mDesign(Design):
    def __init__(self, tilew):
        self.tilew = tilew

    def draw(self, pt, dwg_size, tiler_arg):
        pt.tile_p6m(self.draw_tile, dwg_size, tiler_arg)

    def three_points(self):
        self.top = Point(0, 0)
        self.bottom = Point(0, -self.tilew)
        self.belly = Point(self.tilew * SQRT3 / 4, -self.tilew * .75)

    def draw_triangle(self, dwg):
        self.three_points()
        dwg.move_to(*self.top)
        dwg.line_to(*self.bottom)
        dwg.line_to(*self.belly)
        dwg.close_path()
