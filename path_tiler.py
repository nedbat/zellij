import contextlib

from affine import Affine

from euclid import Point


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
