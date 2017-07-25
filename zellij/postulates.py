"""Simple things we'd like to take for granted, but must be stated."""

import itertools


def adjacent_pairs(seq):
    """From e0, e1, e2, e3, ... produce (e0,e1), (e1,e2), (e2,e3), ..."""
    return zip(seq, itertools.islice(seq, 1, None))


def overlap(start1, end1, start2, end2):
    """Does the range (start1, end1) overlap with (start2, end2)?"""
    # https://nedbatchelder.com/blog/201310/range_overlap_in_two_compares.html
    return end1 >= start2 and end2 >= start1
