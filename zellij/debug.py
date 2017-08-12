"""Debug helpers."""

from zellij.drawing import Drawing
from zellij.euclid import Point


def tick_range(lo, hi, step):
    lo, hi, step = map(int, [lo, hi, step])
    lo = (lo // step) * step
    hi = ((hi // step) + 1) * step
    return range(lo, hi, step)

def debug_world(paths, width, height):
    dwg = Drawing(paths=paths, name="debug_world", bg=None)

    # Gray rectangle: the desired visible canvas.
    with dwg.style(rgb=(.95, .95, .95)):
        dwg.rectangle(0, 0, width, height)
        dwg.fill()

    # Reference grid.
    llx, lly = dwg.llx, dwg.lly
    urx = llx + dwg.width
    ury = lly + dwg.height
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
