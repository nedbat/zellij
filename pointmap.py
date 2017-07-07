"""
A map with Points as the keys.
"""

from euclid import Point


class PointMap:
    """
    Like a defaultdict, but with Points as keys.

    Points compare inexactly, so misses have to be checked with a linear
    search.  The values are constructed with the factory.
    """

    def __init__(self, factory):
        self._items = {}        # maps points to values
        self._grida = {}        # maps rounded points to points
        self._gridb = {}
        self._factory = factory

    def _round(self, pt, alt=False):
        x, y = pt
        if alt:
            x += 0.0005
            y += 0.0005
        x = round(x, ndigits=3)
        y = round(y, ndigits=3)
        return Point(x, y)

    def __getitem__(self, pt):
        val = self._find(pt)
        if val is None:
            # Really didn't find it: make one.
            val = self._factory()
            self._set(pt, val)
        return val

    def _find(self, pt):
        val = self._items.get(pt)
        if val is not None:
            return val

        # Check the grid
        pta = self._round(pt)
        pt0 = self._grida.get(pta)
        if pt0 is not None:
            return self._items[pt0]

        # Check the alt grid.
        ptb = self._round(pt, alt=True)
        pt0 = self._gridb.get(ptb)
        if pt0 is not None:
            return self._items[pt0]

        return None

    def _set(self, pt, val):
        self._items[pt] = val
        self._grida[self._round(pt)] = pt
        self._gridb[self._round(pt, alt=True)] = pt
        return val

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, key):
        val = self._find(key)
        return val is not None

    def items(self):
        return self._items.items()
