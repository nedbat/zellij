from zellij.drawing import Drawing
from zellij.path_tiler import combine_paths, replay_path, PathTiler
from zellij.strap import strapify

from zellij.design.threestars import ThreeStarsDesign


DWGW = 800

TILEW = int(DWGW/3)
if 0:
    strap_kwargs = dict(width=TILEW / 60, random_factor=4.9)
else:
    strap_kwargs = dict(width=TILEW / 15, random_factor=0)

pt = PathTiler()
draw = ThreeStarsDesign(TILEW)
draw.draw(pt, (DWGW, DWGW), TILEW)
paths = pt.paths
paths = combine_paths(pt.paths)
paths = [tuple(path) for path in paths]

straps = strapify(paths, **strap_kwargs)

dwg = Drawing(DWGW, DWGW, name="straps", bg=(.8, .8, .8))

with dwg.style(rgb=(1, 1, 1)):
    for strap in straps:
        replay_path(strap.sides[0], dwg)
        replay_path(strap.sides[1][::-1], dwg, start=False)
        dwg.close_path()
        dwg.fill()

with dwg.style(rgb=(0, 0, 0), width=2):
    for strap in straps:
        for side in strap.sides:
            replay_path(side, dwg)
            dwg.stroke()

dwg.finish()
