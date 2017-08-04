"""Command-line interface for Zellij."""

import click

from zellij.design import get_design
from zellij.drawing import Drawing
from zellij.path_tiler import combine_paths, replay_path, PathTiler
from zellij.strap import strapify


_common_options = {
    'drawing': [
        click.option('--output', default='drawing.png', help='File name to write to'),
        click.option('--tiles', type=float, default=4, help='How many tiles to fit in the drawing'),
        click.option('--size', default='dsize'),
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
def main():
    pass

@main.command()
@common_options('drawing')
@click.option("--strap-width", type=float, default=6, help='Width of the strap, in tile-percent')
def straps(**opt):
    DWGW = 800

    TILEW = int(DWGW/opt['tiles'])
    if opt['strap_width'] < 0:
        strap_kwargs = dict(width=TILEW / 60, random_factor=4.9)
    else:
        strap_kwargs = dict(width=TILEW * opt['strap_width'] / 100, random_factor=0)

    dwg = Drawing(DWGW, DWGW, name="straps", bg=(.8, .8, .8))
    pt = PathTiler()
    design_class = get_design(opt['design'])
    draw = design_class(TILEW)
    draw.draw(pt, dwg.get_size())
    paths = combine_paths(pt.paths)

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

@main.command()
@common_options('drawing')
def two(**kwargs):
    print(kwargs)
    print('two')
