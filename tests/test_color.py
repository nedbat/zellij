"""
Test zellij/color.py
"""

import pytest

from zellij.color import parse_color, rgb255

HALF = 0.5019607843137255

@pytest.mark.parametrize("r, g, b, result", [
    (0, 0, 0, (0, 0, 0)),
    (255, 0, 128, (1, 0, HALF)),
])
def test_rgb255(r, g, b, result):
    assert rgb255(r, g, b) == result


@pytest.mark.parametrize("s, result", [
    ("none", ()),
    ("white", (1, 1, 1)),
    ("red", (1, 0, 0)),
    ("green", (0, HALF, 0)),
    ("#000", (0, 0, 0)),
    ("#887766", (0.5333333333333333, 0.4666666666666667, .4)),
])
def test_parse_color(s, result):
    assert parse_color(s) == result
