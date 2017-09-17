"""Simple things we'd like to take for granted, but must be stated."""

import itertools
import math
import random


def isclose(a, b):
    """Are two floats close together, even near zero."""
    return math.isclose(a, b, abs_tol=1e-8)


def adjacent_pairs(seq):
    """From e0, e1, e2, e3, ... produce (e0,e1), (e1,e2), (e2,e3), ..."""
    return zip(seq, itertools.islice(seq, 1, None))


def all_pairs(seq):
    """Produce all pairs from seq, but not (a, a)"""
    return itertools.combinations(seq, 2)


def triples(seq):
    """Iterate over the triples of consecutive elements in seq (possibly circular)."""
    # Take care to include the triples across the ends if the sequence is a loop.
    if seq[0] == seq[-1]:
        seq = seq + seq[1:2]
    return zip(seq, seq[1:], seq[2:])


def overlap(start1, end1, start2, end2):
    """Does the range (start1, end1) overlap with (start2, end2)?"""
    # https://nedbatchelder.com/blog/201310/range_overlap_in_two_compares.html
    if start1 > end1:
        start1, end1 = end1, start1
    if start2 > end2:
        start2, end2 = end2, start2
    return end1 >= start2 and end2 >= start1


def fbetween(a, b, c):
    """Is float `b` between floats `a` and `c`?"""
    if a <= b <= c or a >= b >= c:
        return True
    else:
        return isclose(a, b) or isclose(b, c)


def perturbed(v, jitter):
    """Return `v`, with -jitter..jitter randomly added."""
    return v + 2*jitter * random.random() - jitter
