"""Command-line interface for Zellij."""

import pprint

import click

from zellij.color import random_color
from zellij.debug import debug_world, debug_click_options, should_debug
from zellij.design import get_design
from zellij.drawing import Drawing
from zellij.path_tiler import combine_paths, replay_path, PathTiler
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
        click.option('--format', default='png'),
        click.argument('design'),
    ],
}

def common_options(category):
    def _wrapper(func):
        # from: https://github.com/pallets/click/issues/108#issuecomment-194465429
        for option in reversed(_common_options[category]):
            func = option(func)
        return func
    return _wrapper

@click.group()
def clickmain():
    pass


@clickmain.command()
@common_options('common')
@common_options('drawing')
@click.option("--strap-width", type=float, default=6, help='Width of the straps, in tile-percent')
def straps(**opt):
    width, height = opt['size']

    TILEW = int(width/opt['tiles'])
    if opt['strap_width'] > 0:
        strap_kwargs = dict(width=TILEW * opt['strap_width'] / 100, random_factor=0)
    else:
        strap_kwargs = dict(width=TILEW / 60, random_factor=4.9)

    dwg = Drawing(width, height, name="straps", bg=(.8, .8, .8))
    pt = PathTiler()
    design_class = get_design(opt['design'])
    draw = design_class(TILEW)
    draw.draw(pt, dwg.get_size())
    paths = combine_paths(pt.paths)

    if should_debug('world'):
        debug_world(paths, width, height)

    straps = strapify(paths, **strap_kwargs)

    with dwg.style(rgb=(1, 1, 1)):
        for strap in straps:
            replay_path(strap.sides[0], dwg)
            replay_path(strap.sides[1][::-1], dwg, append=True)
            dwg.close_path()
            dwg.fill()

    with dwg.style(rgb=(0, 0, 0), width=2):
        for strap in straps:
            for side in strap.sides:
                replay_path(side, dwg)
                dwg.stroke()

    dwg.finish()

@clickmain.command()
@common_options('common')
@common_options('drawing')
def candystripe(**opt):
    width, height = opt['size']

    TILEW = int(width/opt['tiles'])

    dwg = Drawing(width, height, name="candy")
    pt = PathTiler()
    design_class = get_design(opt['design'])
    draw = design_class(TILEW)
    draw.draw(pt, dwg.get_size())
    paths = combine_paths(pt.paths)

    LINE_WIDTH = TILEW/4

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
def show_opts(**opt):
    pprint.pprint(opt)


def main():
    # A Python main so we can eventually do some clean top-level exception handling.
    try:
        clickmain()
    except:
        #print("Whoops!")
        raise


if __name__ == '__main__':
    main()
