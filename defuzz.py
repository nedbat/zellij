"""
De-fuzz tuples of floats.
"""

import itertools


class Defuzzer:
    """
    Remove the fuzz from a collection of points (float tuples).

    Call `defuzz` with a tuple of floats. It will return a tuple of floats
    which are close enough to the input.  The returned value will be either the
    same as the input, or will be a previously seen tuple which is close to the
    input.

    The `ndigits` argument defines closeness.  `10 ** -ndigits` is the window
    size.  Numbers within `0.5 * window` of each other are guaranteed to be
    compared equal.  Numbers that are `1.5 * window` apart or more are
    guaranteed to be compared different.
    """

    def __init__(self, ndigits=6):
        self.ndigits = ndigits
        self.points = set()     # the set of good points
        self.rounds = {}        # maps rounded points to good points
        self.jitters = [0, 0.5 * 10 ** -self.ndigits]

    def roundings(self, pt):
        """Produce the different roundings of `pt`."""
        for jitter in itertools.product(self.jitters, repeat=len(pt)):
            yield tuple(round(v + j, ndigits=self.ndigits) for v, j in zip(pt, jitter))

    def defuzz(self, pt):
        if pt in self.points:
            return pt

        # Check the rounded points.
        roundings = list(self.roundings(pt))
        for pt_round in roundings:
            pt0 = self.rounds.get(pt_round)
            if pt0 is not None:
                return pt0

        # This point is new to us.
        self.points.add(pt)
        for pt_round in roundings:
            self.rounds[pt_round] = pt

        return pt
