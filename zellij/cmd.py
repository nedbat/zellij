"""Command-line interface for Zellij."""

import math
import pprint

import click

from zellij.color import random_color, parse_color
from zellij.debug import debug_world, debug_click_options, should_debug
from zellij.design import get_design
from zellij.drawing import Drawing
from zellij.path import combine_paths, draw_paths, clip_paths
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
        click.option('--output', help='File name to write to'),
        click.option('--tiles', type=float, default=3, help='How many tiles to fit in the drawing'),
        click.option('--size', type=size_type, default='800', help='Size of the output'),
        click.option('--rotate', type=float, default=0, help='Angle to rotate the drawing'),
        click.option('--background', type=parse_color, help='The color of the background'),
        click.option('--format', help='The output format, png or svg'),
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

    bg = opt['background']
    def_bg = drawing_args.pop('bg', (1, 1, 1))
    if bg is None:
        bg = def_bg

    name = opt['output']
    def_name = drawing_args.pop('name', 'drawing')
    format = opt['format']

    dwg = Drawing(width, height, name=name or def_name, format=format, bg=bg, **drawing_args)
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

    tiler = PathTiler(dwg)
    design_class = get_design(opt['design'])
    draw = design_class(tilew)
    draw.draw(tiler)
    paths = combine_paths(tiler.paths)
    paths = clip_paths(paths, dwg.perimeter().bounds())

    if should_debug('world'):
        debug_world(dwg, paths)

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

    tiler = PathTiler(dwg)
    design_class = get_design(opt['design'])
    draw = design_class(tilew)
    draw.draw(tiler)
    paths = combine_paths(tiler.paths)

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
    tiler = PathTiler(dwg)
    draw.draw(tiler)
    with dwg.style(rgb=(.5, .5, .5)):
        draw_paths(tiler.paths, dwg)
        dwg.stroke()

    # The symmetry.
    tiler = PathTiler(dwg)
    tiler.tile_p6m(draw.draw_tiler_unit, tilew)
    with dwg.style(rgb=(1, .75, .75), width=1, dash=[5, 5]):
        draw_paths(tiler.paths, dwg)
        dwg.stroke()

    def single_tiler():
        """Make a PathTiler right for drawing just one unit."""
        tiler = PathTiler(dwg)
        # TODO: make this work for other symmetries
        tiler.pc.translate(2 * tilew * math.sqrt(3) / 2, tilew)
        tiler.pc.reflect_xy(0, 0)
        return tiler

    # The tiler unit.
    tiler = single_tiler()
    draw.draw_tiler_unit(tiler.pc)
    with dwg.style(rgb=(1, 0, 0), width=3):
        draw_paths(tiler.paths, dwg)
        dwg.stroke()

    # The design.
    tiler = single_tiler()
    draw.draw_tile(tiler.pc)
    with dwg.style(rgb=(0, 0, 0), width=6):
        draw_paths(tiler.paths, dwg)
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
