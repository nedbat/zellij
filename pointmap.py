"""
A map with Points as the keys.
"""

class PointMap:
    """Like a defaultdict, but with Points as keys.

    Points compare inexactly, and so cannot be hashed, so we can't use a
    dict.  This is a dead-simple implementation using a linear search.
    """
    # With more points, we might need a k-d tree: https://en.wikipedia.org/wiki/K-d_tree 

    def __init__(self, factory):
        # A list of (pt, value) tuples.
        self._items = []
        self._factory = factory

    def __getitem__(self, pt):
        for key, value in self._items:
            if key == pt:
                return value

        # Didn't find it, add the point to the end and make a new value.
        value = self._factory()
        self._items.append((pt, value))
        return value

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for key, value in self._items:
            yield key

    def items(self):
        yield from self._items
