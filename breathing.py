import colorsys
import random

from drawing import Drawing
from euclid import Line, Point
from path_tiler import PathTiler
from path_tiler import combine_paths, replay_path

import cairo

DWGW = 800
TILEW = int(DWGW/5)

LINE_WIDTH = TILEW/4
JOIN = True

def draw_tile(dwg):
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

def tile_p1(pt, draw_func, w, h, dx, dy, ox=0, oy=0):
    """Repeatedly call draw_func to tile the drawing."""
    for x in range(int(ox), w, dx):
        for y in range(int(oy), h, dy):
            with pt.saved():
                pt.translate(x, y)
                draw_func(pt)

def tile_pmm(pt, draw_func, w, h, dx, dy):
    def four_mirror(dwg):
        draw_func(pt)
        with pt.saved():
            pt.reflect_x(2*dx)
            draw_func(pt)
        with pt.saved():
            pt.reflect_xy(2*dx, 2*dy)
            draw_func(pt)
        with pt.saved():
            pt.reflect_y(2*dy)
            draw_func(pt)

    tile_p1(pt, four_mirror, w, h, dx*2, dy*2)


dwg = Drawing(DWGW, DWGW)
pt = PathTiler()

tile_pmm(pt, draw_tile, dwg.get_width(), dwg.get_height(), TILEW//2, TILEW//2)

paths = pt.paths
if JOIN:
    paths = combine_paths(paths)

def random_color():
    return colorsys.hls_to_rgb(
        random.choice(range(36))/36,
        random.choice(range(3, 9))/10,
        random.choice(range(6, 11))/10,
    )

styles = [
    #(LINE_WIDTH, (0, 0, 0)),
    (LINE_WIDTH-2, random_color),
    #(7, (0, 0, 0)),
    (5, (1, 1, 1)),
]

dwg.set_line_cap(cairo.LineCap.ROUND)
for width, color in styles:
    dwg.set_line_width(width)
    for path in paths:
        replay_path(path, dwg)
        if callable(color):
            dwg.set_source_rgb(*color())
        else:
            dwg.set_source_rgb(*color)
        dwg.stroke()

dwg.write_to_png('breathing.png')
