import colorsys
import math
import pprint
import random

from drawing import Drawing
from euclid import Line, Point
from path_tiler import PathTiler
from path_tiler import combine_paths, replay_path

import cairo

DWGW = 800
TILEW = int(DWGW/5)
SQW = TILEW/2 * math.sqrt(2)

RAINBOW = True
LINE_WIDTH = TILEW/10
JOIN = True

def draw_tile(dwg):
    dwg.translate(TILEW/2, TILEW/2)

    west = Point(-TILEW/2, 0)
    north = Point(0, TILEW/2)
    northwest = Point(-SQW/2, SQW/2)
    diagonal = Line(west, north)
    vert = Line(Point(-SQW/2, -SQW/2), northwest)
    horz = Line(northwest, Point(SQW/2, SQW/2))

    wnw = diagonal.intersect(vert)
    nnw = diagonal.intersect(horz)

    for angle in range(4):
        with dwg.saved():
            dwg.rotate(angle * 90)
            dwg.move_to(*west)
            dwg.line_to(*wnw)
            dwg.line_to(*northwest)
            dwg.line_to(*nnw)
            dwg.line_to(*north)


def tile(pt, draw_func, w, h, dx, dy, ox=0, oy=0):
    """Repeatedly call draw_func to tile the drawing."""
    for x in range(int(ox), w, dx):
        for y in range(int(oy), h, dy):
            with pt.saved():
                pt.translate(x, y)
                draw_func(pt)

dwg = Drawing(DWGW, DWGW)
pt = PathTiler()

tile(pt, draw_tile, dwg.get_width(), dwg.get_height(), TILEW, TILEW)

paths = pt.paths
if JOIN:
    paths = combine_paths(paths)
    print(f"{len(pt.paths)} paths -> {len(paths)} paths")

def random_color():
    return colorsys.hls_to_rgb(
        random.choice(range(36))/36,
        random.choice(range(3, 9))/10,
        random.choice(range(6, 11))/10,
    )

dwg.set_line_width(LINE_WIDTH)
dwg.set_line_cap(cairo.LineCap.ROUND)
dwg.set_source_rgb(0, 0, 0)
for path in paths:
    replay_path(path, dwg)
    if RAINBOW:
        dwg.set_source_rgb(*random_color())
    dwg.stroke()

dwg.write_to_png('breathing.png')
