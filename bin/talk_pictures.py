"""Produce the pictures for the presentation about Zellij."""

import itertools
import math

from zellij.color import random_color, CasaCeramica
from zellij.drawing import Drawing
from zellij.path import combine_paths, offset_path
from zellij.path_tiler import PathTiler

from zellij.design.threestars import ThreeStarsDesign

SQRT3 = math.sqrt(3)


def draw_it(TILEW, dwg, combined=True, fat=True, color=(0, 0, 0), line_width=2, offset=None):
    pt = PathTiler()
    draw = ThreeStarsDesign(TILEW)
    draw.draw(pt, dwg.get_size())
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

    dwgnum = iter(itertools.count())
    def dwg_name(slug):
        return f'three_stars_{next(dwgnum):03d}_{slug}'

    dwg = Drawing(*size, name=dwg_name('start'), bg=(.85, .85, .85))
    draw_it(TILEW, dwg)
    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('thin'))
    draw_it(TILEW, dwg, fat=False)
    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('symmetry'))
    pt = PathTiler()
    draw = ThreeStarsDesign(TILEW)
    pt.tile_p6m(draw.draw_triangle, dwg.get_size(), TILEW)
    with dwg.style(rgb=(1, .15, .15), width=1, dash=[5, 5]):
        pt.replay_paths(dwg)
        dwg.stroke()
    dwg.finish()

    def single_tiler():
        pt = PathTiler()
        pt.translate(2 * TILEW * SQRT3 / 2, TILEW)
        pt.reflect_xy(0, 0)
        return pt

    dwg = Drawing(*size, name=dwg_name('triangle'))
    pt = PathTiler()
    draw = ThreeStarsDesign(TILEW)
    pt.tile_p6m(draw.draw_triangle, dwg.get_size(), TILEW)
    with dwg.style(rgb=(1, .5, .5), width=1, dash=[5, 5]):
        pt.replay_paths(dwg)
        dwg.stroke()
    pt = single_tiler()
    draw.draw_triangle(pt)
    with dwg.style(rgb=(1, 0, 0), width=3):
        pt.replay_paths(dwg)
        dwg.stroke()
    dwg.finish()

    dwg = Drawing(*size, name=dwg_name('design'))
    pt = PathTiler()
    draw = ThreeStarsDesign(TILEW)
    pt.tile_p6m(draw.draw_triangle, dwg.get_size(), TILEW)
    with dwg.style(rgb=(1, .5, .5), width=1, dash=[5, 5]):
        pt.replay_paths(dwg)
        dwg.stroke()
    pt = single_tiler()
    draw.draw_triangle(pt)
    with dwg.style(rgb=(1, 0, 0), width=3):
        pt.replay_paths(dwg)
        dwg.stroke()
    pt = single_tiler()
    draw.draw_tile(pt)
    with dwg.style(rgb=(0, 0, 0), width=6):
        pt.replay_paths(dwg)
        dwg.stroke()
    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('lined'))
    draw_it(TILEW, dwg, fat=False, color=(.5, .5, .5))

    pt = PathTiler()
    draw = ThreeStarsDesign(TILEW)
    pt.tile_p6m(draw.draw_triangle, dwg.get_size(), TILEW)
    with dwg.style(rgb=(1, .75, .75), width=1, dash=[5, 5]):
        pt.replay_paths(dwg)
        dwg.stroke()

    pt = single_tiler()
    draw.draw_tile(pt)
    with dwg.style(rgb=(0, 0, 0), width=6):
        pt.replay_paths(dwg)
        dwg.stroke()

    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('chaos'))
    draw_it(TILEW, dwg, fat=False, color=random_color, combined=False, line_width=8)
    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('joined'))
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
