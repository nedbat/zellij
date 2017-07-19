"""
De-fuzz tuples of floats.
"""


class Defuzzer:
    """
    Like a defaultdict, but with Points as keys.

    Points compare inexactly, so a simple dict with points as keys won't work.

    We get constant-time behavior by storing points three ways: as-is, and
    rounded two different ways.  If any of those three maps finds the point,
    then we have a hit.  This works because Zellij will either have points very
    close together (a match), or not (a miss). We don't have to deal with
    points close together that shouldn't be considered the same.
    """

    def __init__(self, round_digits=6):
        self.round_digits = round_digits
        self.points = set()     # the set of good points
        self.rounds = {}        # maps rounded tuples to good tuples

    def roundeds(self, pt):
        """Produce the different roundings of `pt`."""
        for jitter in [0, 0.5 * 10 ** -self.round_digits]:
            yield tuple(round(v + jitter, ndigits=self.round_digits) for v in pt)

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
