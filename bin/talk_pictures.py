import math

from zellij.color import random_color, CasaCeramica
from zellij.drawing import Drawing
from zellij.path_tiler import combine_paths, offset_path, PathTiler

from zellij.design.threestars import ThreeStarsDesign

SQRT3 = math.sqrt(3)


def draw_it(TILEW, dwg, combined=True, fat=True, color=(0, 0, 0), line_width=2, offset=None):
    pt = PathTiler()
    draw = ThreeStarsDesign(TILEW)
    draw.draw(pt, dwg.get_size(), TILEW)
    paths = pt.paths
    if combined:
        paths = combine_paths(pt.paths)
    if offset is not None:
        paths = [offset_path(p, offset) for p in paths]

    if fat:
        LINE_WIDTH = TILEW / 12
        styles = [
            (LINE_WIDTH, (0, 0, 0)),
            (LINE_WIDTH*.7, (1, 1, 1)),
        ]
    else:
        styles = [(line_width, color)]
    dwg.multi_stroke(paths, styles)


DWGW = 800

def talk_pictures():
    size = (883, 683)
    TILEW = int(DWGW/3)

    dwg = Drawing(*size, name='three_stars_0', bg=(.85, .85, .85))
    draw_it(TILEW, dwg)
    dwg.finish()


    dwg = Drawing(*size, name='three_stars_1_thin')
    draw_it(TILEW, dwg, fat=False)
    dwg.finish()


    dwg = Drawing(*size, name='three_stars_2_lined')
    draw_it(TILEW, dwg, fat=False, color=(.8, .8, .8))

    pt = PathTiler()
    draw = ThreeStarsDesign(TILEW)
    pt.tile_p6m(draw.draw_triangle, dwg.get_size(), TILEW)
    with dwg.style(rgb=(1, 0, 0), width=2, dash=[5, 5]):
        pt.replay_paths(dwg)
        dwg.stroke()

    pt = PathTiler()
    pt.translate(2 * TILEW * SQRT3 / 2, TILEW)
    pt.reflect_xy(0, 0)
    draw.draw_tile(pt)
    with dwg.style(rgb=(0, 0, 0), width=6):
        pt.replay_paths(dwg)
        dwg.stroke()

    dwg.finish()


    dwg = Drawing(*size, name='three_stars_3_chaos')
    draw_it(TILEW, dwg, fat=False, color=random_color, combined=False, line_width=8)
    dwg.finish()


    dwg = Drawing(*size, name='three_stars_4_joined')
    draw_it(TILEW, dwg, fat=False, color=random_color, combined=True, line_width=8)
    dwg.finish()

def final():
    TILEW = int(DWGW/5)

    dwg = Drawing(DWGW, DWGW, bg=(.85, .85, .85), name='three_stars_final')
    draw_it(TILEW, dwg)
    dwg.finish()


if __name__ == '__main__':
    talk_pictures()
    final()
