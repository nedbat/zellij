# A face of tajra's dodecahedron
# https://www.instagram.com/tajra.wd/p/DMVSwwmoHVJ/

import contextlib
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
                            MS * P_SHOULDER_WIDTH / 2
                            + SS * P_SHOULDER_WIDTH
                            + SS * ARM_EDGE,
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


@contextlib.contextmanager
def on_p1_p2(dwg, pt1, pt2):
    with dwg.saved():
        dwg.translate(*pt1)
        dwg.rotate(degrees(atan2(pt2[1] - pt1[1], pt2[0] - pt1[0])))
        yield None


def one_face(dwg, LS, pt1, pt2, face_fn):
    """Draw one face with an LS-long edge on (pt1, pt2), return all the vertex points."""
    with on_p1_p2(dwg, pt1, pt2):
        face_fn(dwg, LS)
        pts = [
            dwg.user_to_device(0, 0),
            dwg.user_to_device(LS, 0),
            dwg.user_to_device(LS * (1 + P_SHOULDER_HANG), LS * P_SHOULDER_HEIGHT),
            dwg.user_to_device(LS / 2, LS * P_HEIGHT),
            dwg.user_to_device(-LS * P_SHOULDER_HANG, LS * P_SHOULDER_HEIGHT),
        ]

    return [Point(*dwg.device_to_user(*pt)) for pt in pts]


def tab(dwg, LS, pt1, pt2, has_left, has_right, label=None):
    TAB_WIDTH = 16
    GAP = 1
    SHORT_DIST = TAB_WIDTH / tan(radians(36)) + 2 * GAP
    with on_p1_p2(dwg, pt1, pt2):
        with dwg.style(rgb=(0.75, 0.75, 0.75), width=0.25):
            if has_left:
                dwg.move_to(GAP, GAP)
                dwg.line_to(TAB_WIDTH, TAB_WIDTH)
            else:
                dwg.move_to(SHORT_DIST, TAB_WIDTH)
            if has_right:
                dwg.line_to(LS - TAB_WIDTH, TAB_WIDTH)
                dwg.line_to(LS - GAP, GAP)
            else:
                dwg.line_to(LS - SHORT_DIST, TAB_WIDTH)
            dwg.stroke()

            if label:
                x_move = dwg.text_extents(label).x_advance
                dwg.move_to(LS / 2 - x_move / 2, TAB_WIDTH / 3)
                with dwg.saved():
                    dwg.scale(1, -1)
                    dwg.show_text(label)


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

    def tabc(p1, p2, label=None):
        tab(dwg, LS, p1, p2, True, True, label=label)

    def tabr(p1, p2, label=None):
        tab(dwg, LS, p1, p2, False, True, label=label)

    def tabl(p1, p2, label=None):
        tab(dwg, LS, p1, p2, True, False, label=label)

    tabc(pent0[1], pent0[0], "L")
    tabr(pent0[2], pent0[1], "C")
    tabc(pent0[0], pent0[4], "N")
    tabc(pent2[3], pent2[2], "K")
    tabc(pent2[4], pent2[3], "I")
    tabr(pent2[0], pent2[4], "D")
    tabc(pent3[3], pent3[2], "H")
    tabc(pent3[4], pent3[3], "F")
    tabl(pent4[2], pent4[1], "E")
    tabc(pent4[4], pent4[3], "S")
    tabr(pent4[0], pent4[4], "A")
    tabc(pent5[3], pent5[2], "R")
    tabc(pent5[4], pent5[3], "O")
    tabr(pent5[0], pent5[4], "B")
    tabr(pent6[3], pent6[2], "G")
    tabl(pent6[0], pent6[4], "Q")
    tabr(pent8[0], pent8[4], "J")
    tabr(pent9[0], pent9[4], "M")
    tabr(pent10[0], pent10[4], "P")


# Paper coordinates: pts, origin lower-left.
dwg = Drawing(width=612, height=792, name="tajra.pdf")
dwg.translate(0, 792)
dwg.scale(1, -1)

if 0:
    # Border the printable region
    with dwg.style(rgb=(0.75, 0.75, 0.75), width=0.25, dash=[10, 5]):
        qinch = 72 / 4
        dwg.move_to(qinch, qinch)
        dwg.line_to(612 - qinch, qinch)
        dwg.line_to(612 - qinch, 792 - qinch)
        dwg.line_to(qinch, 792 - qinch)
        dwg.close_path()
        dwg.stroke()

with dwg.saved():
    dwg.translate(140, 36)
    dwg.set_line_width(0.25)

    dodeca_net(dwg, 98, face)

with dwg.saved():
    dwg.translate(72, 792 - 36)
    dwg.rotate(270)
    dwg.scale(1, -1)
    for yline, text in enumerate(
        [
            "A dodecahedron design by Taj Ragoo: @tajra on Instagram",
            "Cut, fold, and glue the tabs in order",
            "https://nedbatchelder.com/blog/202606/dodecahedron_with_stars",
        ]
    ):
        dwg.move_to(0, yline * 12)
        dwg.show_text(text)


dwg.finish()
