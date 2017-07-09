"""
A map with Points as the keys.
"""

from euclid import Point


class PointMap:
    """
    Like a defaultdict, but with Points as keys.

    Points compare inexactly, so a simple dict with points as keys won't work.

    We get constant-time behavior by storing points three ways: as-is, and
    rounded two different ways.  If any of those three maps finds the point,
    then we have a hit.  This works because Zellij will either have points very
    close together (a match), or not (a miss). We don't have to deal with
    points close together that shouldn't be considered the same.
    """

    def __init__(self, factory):
        self._items = {}        # maps points to values
        self._rounded = {}      # maps rounded points to points
        self._factory = factory

    ROUND_DIGITS = 6
    JITTERS = [0, 0.5 * 10 ** -ROUND_DIGITS]

    def _round(self, pt, jitter):
        """Round the point, with a little bit of jitter added."""
        rx = round(pt.x + jitter, ndigits=self.ROUND_DIGITS)
        ry = round(pt.y + jitter, ndigits=self.ROUND_DIGITS)
        return Point(rx, ry)

    def __getitem__(self, pt):
        val = self._get(pt)
        if val is None:
            # Really didn't find it: make one.
            val = self._factory()
            self._set(pt, val)
        return val

    def _get(self, pt):
        """Get the value for `pt`, if any."""
        val = self._items.get(pt)
        if val is not None:
            return val

        # Check the rounded points
        for jitter in self.JITTERS:
            pt_round = self._round(pt, jitter)
            pt0 = self._rounded.get(pt_round)
            if pt0 is not None:
                return self._items[pt0]

        return None

    def _set(self, pt, val):
        """Set the value for `pt`."""
        self._items[pt] = val
        for jitter in self.JITTERS:
            self._rounded[self._round(pt, jitter)] = pt

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, key):
        val = self._get(key)
        return val is not None

    def items(self):
        return self._items.items()
