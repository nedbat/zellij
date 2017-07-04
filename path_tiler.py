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

    def scale(self, x, y):
        self.transform *= Affine.scale(x, y)

    def reflect_x(self, x):
        self.translate(x, 0)
        self.scale(-1, 1)
        self.translate(-x, 0)

    def reflect_y(self, y):
        self.translate(0, y)
        self.scale(1, -1)
        self.translate(0, -y)

    def reflect_xy(self, x, y):
        self.reflect_x(x)
        self.reflect_y(y)

    def reflect_line(self, p1, p2):
        """Reflect across the line from p1 to p2."""
        # https://en.wikipedia.org/wiki/Transformation_matrix#Reflection
        (p1x, p1y), (p2x, p2y) = p1, p2
        dx = p2x - p1x
        dy = p2y - p1y
        denom = dx * dx + dy * dy

        self.translate(p1x, p1y)
        self.transform *= Affine(
            (dx * dx - dy * dy) / denom, (2 * dx * dy) / denom,       0,
            (2 * dx * dy) / denom,       (dy * dy - dx * dx) / denom, 0,
        )
        self.translate(-p1x, -p1y)

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

    # Tiling of draw functions.
    # http://www.quadibloc.com/math/images/wall17.gif
    # https://www.math.toronto.edu/drorbn/Gallery/Symmetry/Tilings/Sanderson/index.html

    def tile_p1(self, draw_func, w, h, dx, dy, ox=0, oy=0):
        """Repeatedly call draw_func to tile the drawing."""
        for x in range(int(ox), w, dx):
            for y in range(int(oy), h, dy):
                with self.saved():
                    self.translate(x, y)
                    draw_func(self)

    def tile_pmm(self, draw_func, w, h, dx, dy):
        def four_mirror(pt):
            draw_func(pt)
            with pt.saved():
                pt.reflect_x(dx)
                draw_func(pt)
            with pt.saved():
                pt.reflect_xy(dx, dy)
                draw_func(pt)
            with pt.saved():
                pt.reflect_y(dy)
                draw_func(pt)

        self.tile_p1(four_mirror, w, h, dx*2, dy*2)

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

def show_path(path):
    if path is None:
        return "None"
    return f"Path[{path[0]}..{len(path)}..{path[-1]}]@{id(path)}"

def show_paths(paths):
    ret = "[\n"
    for path in paths:
        ret += f"    {show_path(path)}\n"
    ret += "]"
    return ret

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
            if not possibilities:
                break
            other = best_join(path, target, possibilities)
            if other is not None:
                used.add(id(path))
                used.add(id(other))
                path = join_paths(path, other)
                pm[path[0]].append(path)
                pm[path[-1]].append(path)
            else:
                break

        combined.append(path)

    return combined
