"""
A convenience wrapper around Cairo.
"""

import colorsys
import contextlib
import random

import cairo

from path_tiler import replay_path


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

    def get_size(self):
        return (self.get_width(), self.get_height())

    def multi_stroke(self, paths, styles):
        for width, color in styles:
            self.set_line_width(width)
            for path in paths:
                replay_path(path, self)
                if callable(color):
                    self.set_source_rgb(*color())
                else:
                    self.set_source_rgb(*color)
                self.stroke()


def random_color():
    return colorsys.hls_to_rgb(
        random.choice(range(36))/36,
        random.choice(range(3, 9))/10,
        random.choice(range(6, 11))/10,
    )
