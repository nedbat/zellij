"""Produce the pictures for the presentation about Zellij."""

import itertools
import math

from zellij.color import random_color
from zellij.drawing import Drawing
from zellij.path import combine_paths, draw_paths
from zellij.path_tiler import PathTiler

from zellij.design.threestars import ThreeStarsDesign

SQRT3 = math.sqrt(3)


def draw_it(tilew, dwg, combined=True, fat=True, color=(0, 0, 0), line_width=2, offset=None):
    pt = PathTiler(dwg)
    draw = ThreeStarsDesign(tilew)
    draw.draw(pt)
    paths = pt.paths
    if combined:
        paths = combine_paths(pt.paths)
    if offset is not None:
        paths = [p.offset_path(offset) for p in paths]

    if fat:
        line_width = tilew / 12
        styles = [
            (line_width, (0, 0, 0)),
            (line_width*.7, (1, 1, 1)),
        ]
    else:
        styles = [(line_width, color)]
    dwg.multi_stroke(paths, styles)


DWGW = 800

def talk_pictures():
    size = (883, 683)
    tilew = int(DWGW/3)

    dwgnum = iter(itertools.count())
    def dwg_name(slug):
        return f'three_stars_{next(dwgnum):03d}_{slug}'

    dwg = Drawing(*size, name=dwg_name('start'), bg=(.85, .85, .85))
    draw_it(tilew, dwg)
    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('thin'))
    draw_it(tilew, dwg, fat=False)
    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('symmetry'))
    pt = PathTiler(dwg)
    draw = ThreeStarsDesign(tilew)
    pt.tile_p6m(draw.draw_tiler_unit, tilew)
    with dwg.style(rgb=(1, .15, .15), width=1, dash=[5, 5]):
        draw_paths(pt.paths, dwg)
        dwg.stroke()
    dwg.finish()

    def single_tiler():
        pt = PathTiler(dwg)
        pt.pc.translate(2 * tilew * SQRT3 / 2, tilew)
        pt.pc.reflect_xy(0, 0)
        return pt

    dwg = Drawing(*size, name=dwg_name('triangle'))
    pt = PathTiler(dwg)
    draw = ThreeStarsDesign(tilew)
    pt.tile_p6m(draw.draw_tiler_unit, tilew)
    with dwg.style(rgb=(1, .5, .5), width=1, dash=[5, 5]):
        draw_paths(pt.paths, dwg)
        dwg.stroke()
    pt = single_tiler()
    draw.draw_tiler_unit(pt.pc)
    with dwg.style(rgb=(1, 0, 0), width=3):
        draw_paths(pt.paths, dwg)
        dwg.stroke()
    dwg.finish()

    dwg = Drawing(*size, name=dwg_name('design'))
    pt = PathTiler(dwg)
    draw = ThreeStarsDesign(tilew)
    pt.tile_p6m(draw.draw_tiler_unit, tilew)
    with dwg.style(rgb=(1, .5, .5), width=1, dash=[5, 5]):
        draw_paths(pt.paths, dwg)
        dwg.stroke()
    pt = single_tiler()
    draw.draw_tiler_unit(pt.pc)
    with dwg.style(rgb=(1, 0, 0), width=3):
        draw_paths(pt.paths, dwg)
        dwg.stroke()
    pt = single_tiler()
    draw.draw_tile(pt.pc)
    with dwg.style(rgb=(0, 0, 0), width=6):
        draw_paths(pt.paths, dwg)
        dwg.stroke()
    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('lined'))
    draw_it(tilew, dwg, fat=False, color=(.5, .5, .5))

    pt = PathTiler(dwg)
    draw = ThreeStarsDesign(tilew)
    pt.tile_p6m(draw.draw_tiler_unit, tilew)
    with dwg.style(rgb=(1, .75, .75), width=1, dash=[5, 5]):
        draw_paths(pt.paths, dwg)
        dwg.stroke()

    pt = single_tiler()
    draw.draw_tile(pt.pc)
    with dwg.style(rgb=(0, 0, 0), width=6):
        draw_paths(pt.paths, dwg)
        dwg.stroke()

    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('chaos'))
    draw_it(tilew, dwg, fat=False, color=random_color, combined=False, line_width=8)
    dwg.finish()


    dwg = Drawing(*size, name=dwg_name('joined'))
    draw_it(tilew, dwg, fat=False, color=random_color, combined=True, line_width=8)
    dwg.finish()

def final():
    tilew = int(DWGW/5)

    dwg = Drawing(DWGW, DWGW, bg=(.85, .85, .85), name='three_stars_final')
    draw_it(tilew, dwg)
    dwg.finish()


if __name__ == '__main__':
    talk_pictures()
    final()
