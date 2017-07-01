import contextlib

from affine import Affine

from euclid import collinear, Point
from pointmap import PointMap


class PathTiler:
    def __init__(self):
        self.paths = []
        self.transform = Affine.identity()
        self.curpt = None
        self.saved_state = []

    # Path creation.

    def move_to(self, x, y):
        x, y = self.transform * (x, y)
        self.paths.append([])
        self.paths[-1].append(Point(x, y))
        self.curpt = x, y

    def line_to(self, x, y):
        x, y = self.transform * (x, y)
        self.paths[-1].append(Point(x, y))
        self.curpt = x, y

    def rel_line_to(self, dx, dy):
        x, y = ~self.transform * self.curpt
        self.line_to(x + dx, y + dy)

    def close_path(self):
        self.paths[-1].append(self.paths[-1][0])
        self.curpt = None

    # Transformation.

    def translate(self, dx, dy):
        self.transform *= Affine.translation(dx, dy)

    def rotate(self, degrees):
        self.transform *= Affine.rotation(degrees)

    # Save/Restore.

    def save(self):
        self.saved_state.append(self.transform)

    def restore(self):
        self.transform = self.saved_state.pop()

    @contextlib.contextmanager
    def saved(self):
        self.save()
        try:
            yield
        finally:
            self.restore()

    # More stuff.

    def replay_paths(self, ctx):
        for path in self.paths:
            replay_path(path, ctx)


def replay_path(path, ctx):
    ctx.move_to(*path[0])
    for pt in path[1:-1]:
        ctx.line_to(*pt)
    if path[-1] == path[0]:
        ctx.close_path()
    else:
        ctx.line_to(*path[-1])


def penultimate(path, point):
    """The second-to-last point from whichever end ends with `point`."""
    if path[0] == point:
        return path[1]
    else:
        assert path[-1] == point
        return path[-2]

def best_join(path, join_point, possibilities):
    others = [p for p in possibilities if p != path]

    # If there's only one other path, then join to that one.
    if len(others) == 1:
        return others[0]

    # If there's more than one, find one we are collinear with.
    path_pen = penultimate(path, join_point)
    for other in others:
        other_pen = penultimate(other, join_point)
        if collinear(path_pen, join_point, other_pen):
            return other

    return None

def join_paths(p1, p2):
    if p1[-1] == p2[0]:
        return p1 + p2[1:]
    elif p1[-1] == p2[-1]:
        return p1 + p2[-2::-1]
    elif p1[0] == p2[-1]:
        return p2 + p1[1:]
    elif p1[0] == p2[0]:
        return p1[::-1] + p2[1:]
    else:
        return None

def combine_paths(paths):
    pm = PointMap(list)
    for path in paths:
        pm[path[0]].append(path)
        pm[path[-1]].append(path)

    combined = []
    used = set()

    for path in paths:
        if id(path) in used:
            continue
        while True:
            target = path[0]
            possibilities = pm[target]
            possibilities = [p for p in possibilities if id(p) not in used]
            other = best_join(path, target, possibilities)
            used.add(id(path))
            if other is not None:
                used.add(id(other))
                path = join_paths(path, other)
            else:
                break

        combined.append(path)

    return combined
