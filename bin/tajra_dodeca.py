# A face of tajra's dodecahedron
# https://www.instagram.com/tajra.wd/p/DMVSwwmoHVJ/

import itertools
from math import sin, cos, tan, radians, sqrt

from zellij.drawing import Drawing

# Height to center of a pentagon with a base of 1.
P_CENTER_HEIGHT = tan(radians(54)) / 2

# Height of a pentagon with a base of 1.
P_HEIGHT = tan(radians(72)) / 2

# Height of the shoulder (star outstretched arms) of a pentagon with a base of 1.
P_SHOULDER_HEIGHT = cos(radians(18))

# Width of the shoulder (widest part of the pentagon).
P_SHOULDER_WIDTH = 1 + 2 * sin(radians(18))

# Height, base, and edge of one arm of a star in a pentagon with a base of 1.
ARM_HEIGHT = P_HEIGHT - P_SHOULDER_HEIGHT
ARM_BASE = ARM_HEIGHT / P_HEIGHT
ARM_EDGE = sqrt((ARM_BASE / 2) ** 2 + ARM_HEIGHT**2)

def face(dwg, H):
    # The side of the large pentagon.
    LS = H / P_CENTER_HEIGHT
    LS2 = LS / 2

    # Side of the small pentagons that hold the small stars
    SS = LS * (P_SHOULDER_WIDTH / 2 / (2 * ARM_HEIGHT + 4 * P_SHOULDER_HEIGHT))

    # The height and then side of the medium pentagon.
    MH = (LS * P_SHOULDER_WIDTH / 2) - (SS * P_HEIGHT)
    MS = MH / P_HEIGHT

    with dwg.saved():
        for i in range(5):
            if i == 0:
                dwg.move_to(LS2, H)
            dwg.line_to(-LS2, H)
            dwg.rotate(360 / 5)
        dwg.close_path()
        dwg.clip()

        for _ in range(5):
            x = 0
            for dx, dashes in [
                (
                    ARM_HEIGHT,
                    [
                        SS * ARM_BASE / 2,
                        SS * ARM_EDGE * 2,
                        SS * ARM_BASE,
                        SS * ARM_EDGE + MS * ARM_EDGE,
                        MS * ARM_BASE,
                        SS * ARM_EDGE + MS * ARM_EDGE,
                        SS * ARM_BASE,
                        SS * ARM_EDGE + MS * ARM_EDGE,
                    ],
                ),
                (
                    2 * P_SHOULDER_HEIGHT,
                    [
                        MS * ARM_BASE / 2,
                        MS * ARM_EDGE + SS * ARM_EDGE,
                        SS * ARM_BASE,
                        SS * ARM_EDGE * 2,
                        SS * ARM_BASE,
                        SS * ARM_EDGE * 2,
                        SS * ARM_BASE,
                        SS * ARM_EDGE * 3,  # overshoot but who cares
                    ],
                ),
                (
                    2 * ARM_HEIGHT,
                    [
                        MS * P_SHOULDER_WIDTH / 2,
                        SS * ARM_EDGE,
                    ],
                ),
                (
                    2 * P_SHOULDER_HEIGHT - 2 * ARM_HEIGHT,
                    [
                        MS * P_SHOULDER_WIDTH / 2 + SS * P_SHOULDER_WIDTH + SS * ARM_EDGE,
                        MS * ARM_EDGE,
                    ],
                ),
            ]:
                x += SS * dx
                for xx in [x, -x]:
                    y = H
                    for gap, draw in itertools.batched(dashes, 2):
                        y -= gap
                        dwg.move_to(xx, y)
                        y -= draw
                        dwg.line_to(xx, y)
                        dwg.stroke()

            dwg.rotate(360 / 5)

    for _ in range(5):
        # Base of the pentagon
        dwg.move_to(-LS2, H)
        dwg.line_to(LS2, H)
        dwg.stroke()
        dwg.rotate(360 / 5)


dwg = Drawing(width=800, height=800, name="tajra.png")
dwg.translate(400, 400)
dwg.set_line_width(0.25)

face(dwg, 300)

dwg.finish()
