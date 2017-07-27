import pytest

from zellij.postulates import fbetween


@pytest.mark.parametrize("a, b, c, result", [
    (1, 2, 3, True),
    (3, 2, 1, True),
    (2, 1, 3, False),
    (1, 2, 1, False),
    (1, 1, 0, True),
    (0, 1, 1, True),
    (1, 1, 1, True),
    (0, -1.5265566588595902e-16, 0.0, True),
])
def test_fbetween(a, b, c, result):
    assert fbetween(a, b, c) == result
