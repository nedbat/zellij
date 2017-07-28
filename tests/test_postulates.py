import pytest

from zellij.postulates import adjacent_pairs, fbetween, overlap


@pytest.mark.parametrize("seq, result", [
    ([1, 2, 3, 4], [(1, 2), (2, 3), (3, 4)]),
    ([1, 2, 3], [(1, 2), (2, 3)]),
    ([1, 2], [(1, 2)]),
    ([1], []),
    ([], []),
])
def test_adjacent_pairs(seq, result):
    assert list(adjacent_pairs(seq)) == result


@pytest.mark.parametrize("a, b, c, result", [
    (1, 2, 3, True),
    (3, 2, 1, True),
    (2, 1, 3, False),
    (1, 2, 1, False),
    (1, 1, 0, True),
    (0, 1, 1, True),
    (1, 1, 1, True),
    (0, -1.5265566588595902e-16, 0.0, True),
    (0, -1e-16, 1, True),
])
def test_fbetween(a, b, c, result):
    assert fbetween(a, b, c) == result


@pytest.mark.parametrize("s1, e1, s2, e2, result", [
    # Simple cases.
    (0, 5, 1, 6, True),
    (0, 5, 10, 15, False),
    # start and end might be reversed.
    (5, 0, 1, 6, True),
    (0, 5, 6, 1, True),
    (5, 0, 6, 1, True),
    # Ranges touch.
    (0, 5, 5, 10, True),
])
def test_overlap(s1, e1, s2, e2, result):
    assert overlap(s1, e1, s2, e2) == result
