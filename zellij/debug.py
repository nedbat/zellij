"""Debug helpers."""

import re

import click

from zellij.drawing import Drawing, nice_paths_bounds
from zellij.euclid import Point


VALID_DEBUGS = ['opts', 'world', 'strapify']
DEBUGS = []

def debug_type(s):
    # I am certain there's a better way to get click to do this...
    global DEBUGS
    debugs = [sp.strip() for sp in re.split(r"[ ,;]+", s)]
    debugs = [d for d in debugs if d]
    for d in debugs:
        if d not in VALID_DEBUGS:
            raise click.BadOptionUsage(f"--debug={d}?? Choose from {', '.join(VALID_DEBUGS)}")
    DEBUGS = debugs
    return debugs


debug_click_options = [
    click.option('--debug', type=debug_type, default=""),
]

def should_debug(opt):
    """Is `opt` one of the --debug switches provided?"""
    return opt in DEBUGS


def tick_range(lo, hi, step):
    lo, hi, step = map(int, [lo, hi, step])
    lo = (lo // step) * step
    hi = ((hi // step) + 1) * step
    return range(lo, hi, step)

def debug_world(dwg0, paths):
    """Draw a picture of the entire world.

    `dwg0` is the Drawing we're really making.

    `paths` are the paths that comprise the world.
    """

    dwg = Drawing(bounds=nice_paths_bounds(paths), name="debug_world", bg=None)

    # Gray rectangle: the desired visible canvas.
    with dwg.style(rgb=(.95, .95, .95)):
        llx, lly, urx, ury = dwg0.bounds
        dwg.move_to(*dwg0.device_to_user(llx, lly))
        dwg.line_to(*dwg0.device_to_user(urx, lly))
        dwg.line_to(*dwg0.device_to_user(urx, ury))
        dwg.line_to(*dwg0.device_to_user(llx, ury))
        dwg.close_path()
        dwg.fill()

    # Reference grid.
    llx, lly, urx, ury = dwg.bounds
    with dwg.style(rgb=(.5, 1, 1), width=1, dash=[5, 5], dash_offset=7.5):
        for xmin in tick_range(llx, urx, 20):
            dwg.move_to(xmin, lly)
            dwg.line_to(xmin, ury)
            dwg.stroke()
        for ymin in tick_range(lly, ury, 20):
            dwg.move_to(llx, ymin)
            dwg.line_to(urx, ymin)
            dwg.stroke()

    with dwg.style(rgb=(.5, 1, 1), width=1):
        dwg.circle_points([Point(0, 0)], radius=10)
        for xmaj in tick_range(llx, urx, 100):
            dwg.move_to(xmaj, lly)
            dwg.line_to(xmaj, ury)
            dwg.stroke()
        for ymaj in tick_range(lly, ury, 100):
            dwg.move_to(llx, ymaj)
            dwg.line_to(urx, ymaj)
            dwg.stroke()

    # The paths themselves.
    dwg.draw_paths(paths, width=1, rgb=(1, 0, 0))

    dwg.finish()
    print("Wrote debug_world.png")
