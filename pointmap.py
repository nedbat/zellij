"""
A map with Points as the keys.
"""

class PointMap:
    """
    Like a defaultdict, but with Points as keys.

    Points compare inexactly, so misses have to be checked with a linear
    search.  The values are constructed with the factory.
    """
    def __init__(self, factory):
        self._items = {}        # maps points to values
        self._dupes = {}        # maps points to equal points
        self._factory = factory

    def __getitem__(self, pt):
        val = self._items.get(pt)
        if val is not None:
            return val

        # Is it a known dupe?
        pt0 = self._dupes.get(pt)
        if pt0 is not None:
            return self._items[pt0]

        # Didn't find it, it might be a new dupe.
        for pt2, val in self._items.items():
            if pt == pt2:
                self._dupes[pt] = pt2
                return val

        # Really didn't find it: make one.
        val = self._factory()
        self._items[pt] = val
        return val

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def x__contains__(self, key):
        return key in self._items

    def items(self):
        return self._items.items()
