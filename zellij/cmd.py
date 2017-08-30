"""Command-line interface for Zellij."""

import math
import pprint

import click

from zellij.color import random_color
from zellij.debug import debug_world, debug_click_options, should_debug
from zellij.design import get_design
from zellij.drawing import Drawing
from zellij.path import combine_paths, draw_paths
from zellij.path_tiler import PathTiler
from zellij.strap import strapify


def size_type(s):
    """For specifying the size: either WxH, or W (square)"""
    if 'x' in s:
        width, height = s.split('x')
    else:
        width = height = s

    return int(width.strip()), int(height.strip())


_common_options = {
    'common':[
        *debug_click_options,
    ],
    'drawing': [
        click.option('--output', default='drawing.png', help='File name to write to'),
        click.option('--tiles', type=float, default=3, help='How many tiles to fit in the drawing'),
        click.option('--size', type=size_type, default='800', help='Size of the output'),
        click.option('--rotate', type=float, default=0, help='Angle to rotate the drawing'),
        click.option('--format', default='png'),
        click.argument('design'),
    ],
}

def common_options(category):
    """Provide a set of common options to a click command."""
    def _wrapped(func):
        # from: https://github.com/pallets/click/issues/108#issuecomment-194465429
        for option in reversed(_common_options[category]):
            func = option(func)
        return func
    return _wrapped


def start_drawing(opt, **drawing_args):
    """Make a Drawing based on the options passed."""
    width, height = opt['size']
    dwg = Drawing(width, height, **drawing_args)
    dwg.translate(width/2, height/2)
    dwg.rotate(opt['rotate'])
    dwg.translate(-width/2, -height/2)
    return dwg

@click.group()
def clickmain():
    """Make Islamic-inspired geometric art."""
    pass


@clickmain.command()
@common_options('common')
@common_options('drawing')
@click.option("--strap-width", type=float, default=6, help='Width of the straps, in tile-percent')
def straps(**opt):
    """Draw with over-under straps"""
    dwg = start_drawing(opt, name="straps", bg=(.8, .8, .8))

    tilew = int(dwg.width/opt['tiles'])
    if opt['strap_width'] > 0:
        strap_kwargs = dict(width=tilew * opt['strap_width'] / 100, random_factor=0)
    else:
        strap_kwargs = dict(width=tilew / 60, random_factor=4.9)

    pt = PathTiler()
    design_class = get_design(opt['design'])
    draw = design_class(tilew)
    draw.draw(pt, dwg.get_size())
    paths = combine_paths(pt.paths)

    if should_debug('world'):
        debug_world(paths, dwg.width, dwg.height)

    straps = strapify(paths, **strap_kwargs)

    with dwg.style(rgb=(1, 1, 1)):
        for strap in straps:
            strap.sides[0].draw(dwg)
            strap.sides[1].draw(dwg, append=True, reverse=True)
            dwg.close_path()
            dwg.fill()

    with dwg.style(rgb=(0, 0, 0), width=2):
        for strap in straps:
            for side in strap.sides:
                side.draw(dwg)
                dwg.stroke()

    dwg.finish()

@clickmain.command()
@common_options('common')
@common_options('drawing')
def candystripe(**opt):
    """Draw with crazy colors and a white stripe"""
    dwg = start_drawing(opt, name="candy")
    tilew = int(dwg.width/opt['tiles'])

    pt = PathTiler()
    design_class = get_design(opt['design'])
    draw = design_class(tilew)
    draw.draw(pt, dwg.get_size())
    paths = combine_paths(pt.paths)

    LINE_WIDTH = tilew/4

    dwg.multi_stroke(paths, [
        #(LINE_WIDTH, (0, 0, 0)),
        (LINE_WIDTH-2, random_color),
        #(7, (0, 0, 0)),
        (5, (1, 1, 1)),
    ])
    dwg.finish()


@clickmain.command()
@common_options('common')
@common_options('drawing')
def diagram(**opt):
    """Draw the underlying structure of a design"""
    width, height = opt['size']
    tilew = int(width/opt['tiles'])

    dwg = Drawing(width, height, name="diagram")
    design_class = get_design(opt['design'])
    draw = design_class(tilew)

    # The full pattern.
    pt = PathTiler()
    draw.draw(pt, dwg.get_size())
    with dwg.style(rgb=(.5, .5, .5)):
        draw_paths(pt.paths, dwg)
        dwg.stroke()

    # The symmetry.
    pt = PathTiler()
    pt.tile_p6m(draw.draw_tiler_unit, dwg.get_size(), tilew)
    with dwg.style(rgb=(1, .75, .75), width=1, dash=[5, 5]):
        draw_paths(pt.paths, dwg)
        dwg.stroke()

    def single_tiler():
        """Make a PathTiler right for drawing just one unit."""
        pt = PathTiler()
        # TODO: make this work for other symmetries
        pt.translate(2 * tilew * math.sqrt(3) / 2, tilew)
        pt.reflect_xy(0, 0)
        return pt

    # The tiler unit.
    pt = single_tiler()
    draw.draw_tiler_unit(pt)
    with dwg.style(rgb=(1, 0, 0), width=3):
        draw_paths(pt.paths, dwg)
        dwg.stroke()

    # The design.
    pt = single_tiler()
    draw.draw_tile(pt)
    with dwg.style(rgb=(0, 0, 0), width=6):
        draw_paths(pt.paths, dwg)
        dwg.stroke()

    dwg.finish()

@clickmain.command()
@common_options('common')
@common_options('drawing')
def show_opts(**opt):
    """Dump the provided options"""
    pprint.pprint(opt)


def main():
    """The main Zellij entry point."""
    try:
        clickmain()
    except:
        #print("Whoops!")
        raise


if __name__ == '__main__':
    main()
