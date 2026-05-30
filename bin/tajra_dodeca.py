# A face of tajra's dodecahedron
# https://www.instagram.com/tajra.wd/p/DMVSwwmoHVJ/

import itertools
from math import atan2, sin, cos, tan, degrees, radians, sqrt

from zellij.drawing import Drawing
from zellij.euclid import Point

# Height to center of a pentagon with a base of 1.
P_CENTER_HEIGHT = tan(radians(54)) / 2

# Height of a pentagon with a base of 1.
P_HEIGHT = tan(radians(72)) / 2

# Height of the shoulder (star outstretched arms) of a pentagon with a base of 1.
P_SHOULDER_HEIGHT = cos(radians(18))

# Width of the shoulder (widest part of the pentagon).
P_SHOULDER_HANG = sin(radians(18))
P_SHOULDER_WIDTH = 1 + 2 * P_SHOULDER_HANG

# Height, base, and edge of one arm of a star in a pentagon with a base of 1.
ARM_HEIGHT = P_HEIGHT - P_SHOULDER_HEIGHT
ARM_BASE = ARM_HEIGHT / P_HEIGHT
ARM_EDGE = sqrt((ARM_BASE / 2) ** 2 + ARM_HEIGHT**2)

def face(dwg, LS):
    """Draws one face.

    The bottom edge is at (0, 0) and rest on the horizontal axis.
    """

    # The half-side of the large pentagon.
    LS2 = LS / 2

    # The center height of the large pentagon.
    H = LS * P_CENTER_HEIGHT

    # Side of the small pentagons that hold the small stars
    SS = LS * (P_SHOULDER_WIDTH / 2 / (2 * ARM_HEIGHT + 4 * P_SHOULDER_HEIGHT))

    # The height and then side of the medium pentagon.
    MH = (LS * P_SHOULDER_WIDTH / 2) - (SS * P_HEIGHT)
    MS = MH / P_HEIGHT

    with dwg.saved():
        # The rest of the drawing code wants the origin to be the center of
        # the pentagon, so move the origin there
        dwg.translate(LS2, H)

        with dwg.saved():
            for i in range(5):
                if i == 0:
                    dwg.move_to(-LS2, -H)
                dwg.line_to(LS2, -H)
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
                        y = -H
                        for gap, draw in itertools.batched(dashes, 2):
                            y += gap
                            dwg.move_to(xx, y)
                            y += draw
                            dwg.line_to(xx, y)
                            dwg.stroke()

                dwg.rotate(360 / 5)

        with dwg.style(rgb=(0.85, 0.85, 0.85)):
            for _ in range(5):
                # Base of the pentagon
                dwg.move_to(-LS2, -H)
                dwg.line_to(LS2, -H)
                dwg.stroke()
                dwg.rotate(360 / 5)


def one_face(dwg, LS, pt1, pt2, face_fn):
    """Draw one face with an LS-long edge on (pt1, pt2), return three more vertex points."""
    with dwg.saved():
        dwg.translate(*pt1)
        dwg.rotate(degrees(atan2(pt2[1] - pt1[1], pt2[0] - pt1[0])))

        face_fn(dwg, LS)
        pts = [
            dwg.user_to_device(0, 0),
            dwg.user_to_device(LS, 0),
            dwg.user_to_device(LS * (1 + P_SHOULDER_HANG), LS * P_SHOULDER_HEIGHT),
            dwg.user_to_device(LS / 2, LS * P_HEIGHT),
            dwg.user_to_device(-LS * P_SHOULDER_HANG, LS * P_SHOULDER_HEIGHT),
        ]

    return [Point(*dwg.device_to_user(*pt)) for pt in pts]

def dodeca_net(dwg, LS, face_fn):
    """A dodecahedron net.

    The first face is at (0, 0) with a side of LS.
    """
    def face(p1, p2):
        return one_face(dwg, LS, p1, p2, face_fn)

    pent0 = face(Point(0, 0), Point(1, 0))
    pent1 = face(pent0[3], pent0[2])
    pent2 = face(pent1[2], pent1[1])
    pent3 = face(pent1[3], pent1[2])
    pent4 = face(pent1[4], pent1[3])
    pent5 = face(pent1[0], pent1[4])
    pent6 = face(pent4[3], pent4[2])
    pent7 = face(pent6[4], pent6[3])
    pent8 = face(pent7[2], pent7[1])
    pent9 = face(pent7[3], pent7[2])
    pent10 = face(pent7[4], pent7[3])
    pent11 = face(pent7[0], pent7[4])


# Paper coordinates: pts, origin lower-left, but tilted a little.
dwg = Drawing(width=612, height=792, name="tajra.pdf")
dwg.translate(0, 792)
dwg.scale(1, -1)

dwg.translate(306, 396)
dwg.rotate(10)
dwg.translate(-306, -396)

dwg.translate(160, 50)
dwg.set_line_width(0.25)

dodeca_net(dwg, 90, face)

dwg.finish()
