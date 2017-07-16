"""
A convenience wrapper around Cairo.
"""

import contextlib

import cairo

from path_tiler import replay_path


class Drawing:
    def __init__(self, width, height, bg=(1, 1, 1)):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)

        # Start with a solid-color canvas.
        self.set_source_rgb(*bg)
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

    @contextlib.contextmanager
    def line_style(self, rgb=None, width=None, dash=None):
        o_source = self.get_source()
        o_width = self.get_line_width()
        o_dash = self.get_dash()
        try:
            if rgb is not None:
                self.set_source_rgb(*rgb)
            if width is not None:
                self.set_line_width(width)
            if dash is not None:
                self.set_dash(dash)
            yield
        finally:
            self.set_source(o_source)
            self.set_line_width(o_width)
            self.set_dash(*o_dash)
