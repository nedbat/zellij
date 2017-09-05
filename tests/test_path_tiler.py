"""Test path_tiler.py"""

from zellij.euclid import Point
from zellij.path_tiler import PathCanvas
from zellij.path import Path


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
