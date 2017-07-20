"""
De-fuzz tuples of floats.
"""


class Defuzzer:
    """
    Remove the fuzz from a collection of float tuples.

    Call `defuzz` with a tuple of floats. It will return a tuple of floats
    which are close enough to the input.  The returned value will be either the
    same as the input, or will be a previously seen tuple which is close to the
    input.

    The `ndigits` argument defines closeness.  `10 ** -ndigits` is the window
    size.  Numbers within 0.5*window of each other are guaranteed to be compared
    equal.  Numbers that are 1.5*window apart or more are guaranteed to be
    compared different.

    """

    def __init__(self, ndigits=6):
        self.ndigits = ndigits
        self.points = set()     # the set of good points
        self.rounds = {}        # maps rounded tuples to good tuples

    def roundeds(self, pt):
        """Produce the different roundings of `pt`."""
        for jitter in [0, 0.5 * 10 ** -self.ndigits]:
            yield tuple(round(v + jitter, ndigits=self.ndigits) for v in pt)

    def defuzz(self, pt):
        if pt in self.points:
            return pt

        # Check the rounded points.
        rounds = list(self.roundeds(pt))
        for pt_round in rounds:
            pt0 = self.rounds.get(pt_round)
            if pt0 is not None:
                return pt0

        # This point is new to us.
        self.points.add(pt)
        for pt_round in rounds:
            self.rounds[pt_round] = pt

        return pt
