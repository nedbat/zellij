import click

from zellij.drawing import Drawing
from zellij.path_tiler import combine_paths, replay_path, PathTiler
from zellij.strap import strapify

from zellij.design.threestars import ThreeStarsDesign


@click.command()
@click.option("--strap-width", type=float, default=6)
def main(strap_width):
    DWGW = 800

    TILEW = int(DWGW/3)
    if 0:
        strap_kwargs = dict(width=TILEW / 60, random_factor=4.9)
    else:
        strap_kwargs = dict(width=TILEW * strap_width / 100, random_factor=0)

    dwg = Drawing(DWGW, DWGW, name="straps", bg=(.8, .8, .8))
    pt = PathTiler()
    draw = ThreeStarsDesign(TILEW)
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


if __name__ == '__main__':
    main()
