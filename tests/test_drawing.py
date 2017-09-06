"""
Test zellij/drawing.py
"""

import pytest

from zellij.drawing import name_and_format


@pytest.mark.parametrize("name_in, format_in, name_out, format_out", [
    ('foo', None, 'foo.png', 'png'),
    ('foo.png', None, 'foo.png', 'png'),
    ('foo.svg', None, 'foo.svg', 'svg'),
    ('foo.bar', 'svg', 'foo.bar', 'svg'),
    ('foo', 'svg', 'foo.svg', 'svg'),
    ('dir/foo.svg', None, 'dir/foo.svg', 'svg'),
    ('dir/foo', None, 'dir/foo.png', 'png'),
])
def test_name_and_format(name_in, format_in, name_out, format_out):
    name_act, format_act = name_and_format(name_in, format_in)
    assert name_act == name_out
    assert format_act == format_out
