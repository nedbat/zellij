"""Test path_tiler.py"""

from zellij.euclid import Point
from zellij.path_tiler import PathCanvas, square_to_parallelogram
from zellij.path import Path

import pytest


def test_do_nothing():
    pt = PathCanvas()
    assert pt.paths == []


def test_two_segments():
    pt = PathCanvas()
    pt.move_to(100, 100)
    pt.line_to(150, 200)
    pt.move_to(17, 17)
    pt.rel_line_to(100, 200)
    pt.close_path()
    assert pt.paths == [
        Path([Point(100.0, 100.0), Point(150.0, 200.0)]),
        Path([Point(17.0, 17.0), Point(117.0, 217.0), Point(17.0, 17.0)]),
    ]


def test_translation():
    pt = PathCanvas()
    pt.move_to(100, 100)
    pt.translate(1000, 2000)
    pt.line_to(10, 20)
    assert pt.paths == [
        Path([Point(100.0, 100.0), Point(1010.0, 2020.0)]),
    ]


def test_reflect_x():
    pt = PathCanvas()
    pt.move_to(100, 100)
    pt.reflect_x(1000)
    pt.line_to(200, 200)
    assert pt.paths == [
        Path([Point(100.0, 100.0), Point(1800, 200)]),
    ]


def test_reflect_y():
    pt = PathCanvas()
    pt.move_to(100, 100)
    pt.reflect_y(1000)
    pt.line_to(200, 200)
    assert pt.paths == [
        Path([Point(100.0, 100.0), Point(200, 1800)]),
    ]


def test_reflect_xy():
    pt = PathCanvas()
    pt.move_to(100, 100)
    pt.reflect_xy(1000, 2000)
    pt.line_to(200, 200)
    assert pt.paths == [
        Path([Point(100.0, 100.0), Point(1800, 3800)]),
    ]


def test_reflect_line():
    pt = PathCanvas()
    pt.move_to(100, 100)
    pt.reflect_line(Point(50, -50), Point(150, 50))
    pt.line_to(100, 50)
    pt.line_to(100, 100)
    assert pt.paths == [
        Path([Point(100.0, 100.0), Point(150, 0), Point(200, 0)]),
    ]


def test_save_restore():
    pt = PathCanvas()
    pt.move_to(100, 100)
    pt.translate(1000, 2000)
    pt.line_to(10, 20)
    pt.save()
    pt.translate(1, 2)
    pt.move_to(1, 2)
    pt.line_to(2, 4)
    pt.restore()
    pt.move_to(1, 2)
    pt.line_to(2, 4)
    assert pt.paths == [
        Path([Point(100.0, 100.0), Point(1010.0, 2020.0)]),
        Path([Point(1002.0, 2004.0), Point(1003.0, 2006.0)]),
        Path([Point(1001.0, 2002.0), Point(1002.0, 2004.0)]),
    ]


def test_rel_line_to():
    pt = PathCanvas()
    pt.translate(1000, 2000)
    pt.move_to(0, 0)
    pt.rel_line_to(100, 200)
    assert pt.paths == [
        Path([Point(1000.0, 2000.0), Point(1100.0, 2200.0)]),
    ]


@pytest.mark.parametrize("pt1, pt2", [
    ((1, 0), (0, 1)),
    ((2, 0), (0, .3)),
    ((1, 0), (.5, 1)),
    ((2, 0), (.5, 1)),
    ((1, .5), (0, 1)),
    ((1, 0), (.5, .8)),
    ((1.3, .1), (.2, .8)),
])
def test_square_to_paralleogram(pt1, pt2):
    pt12 = tuple(v1 + v2 for v1, v2 in zip(pt1, pt2))
    xform = square_to_parallelogram(pt1, pt2)
    ins = [(0, 0), (1, 0), (0, 1), (1, 1)]
    outs = [(0, 0), pt1, pt2, pt12]
    for i, o in zip(ins, outs):
        pti = Point(*i)
        pto = Point(*o)
        actual = Point(*(xform * pti))
        print(pti, pto, actual)
        assert actual.is_close(pto)
