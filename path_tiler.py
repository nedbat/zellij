import contextlib

from affine import Affine


class Path:
    def __init__(self):
        self.ops = []

    def append(self, op):
        self.ops.append(op)

    def replay(self, ctx):
        for op in self.ops:
            getattr(ctx, op[0])(*op[1:])


class PathTiler:
    def __init__(self):
        self.paths = []
        self.transform = Affine.identity()
        self.curpt = None
        self.saved_state = []

    # Path creation.

    def move_to(self, x, y):
        x, y = self.transform * (x, y)
        newpath = Path()
        self.paths.append(newpath)
        self.paths[-1].append(('move_to', x, y))
        self.curpt = x, y

    def line_to(self, x, y):
        x, y = self.transform * (x, y)
        self.paths[-1].append(('line_to', x, y))
        self.curpt = x, y

    def rel_line_to(self, dx, dy):
        x, y = ~self.transform * self.curpt
        self.line_to(x + dx, y + dy)

    def close_path(self):
        self.paths[-1].append(('close_path',))
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
            path.replay_path(ctx)
