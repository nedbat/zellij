"""
A convenience wrapper around Cairo.
"""

import contextlib
import itertools
import math
import os.path
import sys

import cairo

from .path import paths_box


def name_and_format(name, format):
    """Resolve the filename and format of a drawing.

    `format` is 'png', 'svg', or None. If None, then the file extension of
    `name` is used, or 'png' if there is no extension.

    If `name` is extensionless, then the format is used as the extension.

    """
    name_base, name_ext = os.path.splitext(name)
    if format is None:
        if name_ext:
            format = name_ext.lstrip('.')
        else:
            format = "png"
    if not name_ext:
        name_ext = f".{format}"
    name = name_base + name_ext
    return name, format


class Drawing:
    def __init__(self, width=None, height=None, name=None, paths=None, bg=(1, 1, 1), format=None):
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
            llx = lly = 0

        self.llx, self.lly = llx, lly
        self.width, self.height = width, height

        self.name, self.format = name_and_format(name, format)

        if self.format == 'png':
            self.surface = cairo.ImageSurface(cairo.Format.ARGB32, self.width, self.height)
        elif self.format == 'svg':
            self.surface = cairo.SVGSurface(self.name, self.width, self.height)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_antialias(cairo.Antialias.BEST)
        self.ctx.set_line_cap(cairo.LineCap.ROUND)
        self.ctx.set_line_join(cairo.LineJoin.MITER)

        if paths:
            self.translate(-self.llx, -self.lly)

        # Start with a solid-color canvas.
        if bg:
            with self.style(rgb=bg):
                self.rectangle(self.llx, self.lly, self.width, self.height)
                self.fill()

    def __getattr__(self, name):
        """Use the drawing like a context, or a surface."""
        try:
            return getattr(self.ctx, name)
        except AttributeError:
            return getattr(self.surface, name)

    def _fix_coord(self, v):
        """Adjust a coordinate to get uniformly drawn lines."""
        width = self.get_line_width()
        if width == int(width):
            if width % 2:
                return math.floor(v) + 0.5
            else:
                return round(v)
        else:
            return (math.floor(2 * v) + 0.5) / 2

    def _fix_point(self, x, y):
        """Adjust a point to get uniformly drawn lines."""
        dx, dy = self.ctx.user_to_device(x, y)
        dx = self._fix_coord(dx)
        dy = self._fix_coord(dy)
        x, y = self.ctx.device_to_user(dx, dy)
        return x, y

    def move_to(self, x, y):
        self.ctx.move_to(*self._fix_point(x, y))

    def line_to(self, x, y):
        self.ctx.line_to(*self._fix_point(x, y))

    def rotate(self, degrees):
        # Cairo uses radians, let's be more convenient.
        self.ctx.rotate(degrees * math.pi / 180)

    @contextlib.contextmanager
    def saved(self):
        self.ctx.save()
        try:
            yield
        finally:
            self.ctx.restore()

    def get_size(self):
        return (self.width, self.height)

    def corners(self):
        return self.llx, self.lly, self.llx + self.width, self.lly + self.height

    def circle(self, xc, yc, radius):
        self.arc(xc, yc, radius, 0, math.pi * 2)

    def multi_stroke(self, paths, styles):
        for width, color in styles:
            self.set_line_width(width)
            for path in paths:
                path.draw(self)
                if callable(color):
                    self.set_source_rgb(*color())
                else:
                    self.set_source_rgb(*color)
                self.stroke()

    def finish(self):
        if self.format == 'png':
            self.write_to_png(self.name)
        elif self.format == 'svg':
            self.surface.flush()
            self.surface.finish()

    @contextlib.contextmanager
    def style(self, rgb=None, width=None, dash=None, dash_offset=0):
        """Set and restore the drawing style."""
        o_source = self.get_source()
        o_width = self.get_line_width()
        o_dash = self.get_dash()
        try:
            if rgb is not None:
                self.set_source_rgb(*rgb)
            if width is not None:
                self.set_line_width(width)
            if dash is not None:
                self.set_dash(dash, dash_offset)
            yield
        finally:
            self.set_source(o_source)
            self.set_line_width(o_width)
            self.set_dash(*o_dash)

    def draw_path(self, path, **style_kwargs):
        with self.style(**style_kwargs):
            path.draw(self)
            self.stroke()

    def draw_paths(self, paths, **style_kwargs):
        with self.style(**style_kwargs):
            for path in paths:
                path.draw(self)
            self.stroke()

    def draw_segments(self, segments, **style_kwargs):
        with self.style(**style_kwargs):
            for (x1, y1), (x2, y2) in segments:
                self.move_to(x1, y1)
                self.line_to(x2, y2)
                self.stroke()

    def circle_points(self, points, radius=5, **style_kwargs):
        with self.style(**style_kwargs):
            for x, y in points:
                self.circle(x, y, radius)
                self.stroke()

    def fill_points(self, points, radius=5, **style_kwargs):
        with self.style(**style_kwargs):
            for x, y in points:
                self.circle(x, y, radius)
                self.fill()

    def cross_points(self, points, radius=5, rotate=0, **style_kwargs):
        with self.style(**style_kwargs):
            for x, y in points:
                with self.saved():
                    self.translate(x, y)
                    self.rotate(-rotate)
                    self.move_to(radius, 0)
                    self.line_to(2 * radius, 0)
                    self.move_to(-radius, 0)
                    self.line_to(-2 * radius, 0)
                    self.move_to(0, radius)
                    self.line_to(0, 2 * radius)
                    self.move_to(0, -radius)
                    self.line_to(0, -2 * radius)
                    self.stroke()


class DrawingSequence:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        nums = itertools.count()
        while True:
            num = next(nums)
            name = self.name.replace("_", f"_{num:04d}")
            dwg = Drawing(name=name, *self.args, **self.kwargs)
            dwg.num = num
            sys.stdout.write(".")
            sys.stdout.flush()
            yield dwg
