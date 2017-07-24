"""
A convenience wrapper around Cairo.
"""

import contextlib
import math

import cairo

from .path_tiler import replay_path, paths_box


class Drawing:
    def __init__(self, width=None, height=None, paths=None, bg=(1, 1, 1)):
        """Create a new Cairo drawing.

        If `paths` is provided, the drawing is sized and positioned so that all
        of the paths are included.  Otherwise, provide `width` and `height` to
        specify a size explicitly.

        `bg` is the background color to paint initially.

        """
        if paths:
            (llx, lly), (urx, ury) = paths_box(paths)
            dx = urx - llx
            dy = ury - lly
            margin = max(dx, dy) * .02
            urx += margin
            ury += margin
            llx -= margin
            lly -= margin
            width, height = int(urx - llx), int(ury - lly)
        else:
            assert width is not None
            assert height is not None

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)

        if paths:
            self.translate(-llx, -lly)

        # Start with a solid-color canvas.
        if bg is not None:
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

    def circle(self, xc, yc, radius):
        self.arc(xc, yc, radius, 0, math.pi * 2 - .001)

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
