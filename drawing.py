import contextlib

import cairo


class Drawing:
    def __init__(self, width, height):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)

        # Start with a white canvas.
        self.set_source_rgb(1, 1, 1)
        self.set_operator(cairo.OPERATOR_SOURCE)
        self.paint()

    def __getattr__(self, name):
        """Use the drawing like a context, or a surface."""
        try:
            return getattr(self.ctx, name)
        except AttributeError:
            return getattr(self.surface, name)

    @contextlib.contextmanager
    def saved(self):
        self.ctx.save()
        try:
            yield
        finally:
            self.ctx.restore()
