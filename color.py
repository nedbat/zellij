"""
Color support for Zellij.
"""

import colorsys
import random


def color255(r, g, b):
    """Define an RGB color with three values 0..255."""
    return (r/255, g/255, b/255)


def lighten(color, pct):
    """Make a color `pct` percent lighter."""
    h, l, s = colorsys.rgb_to_hls(*color)
    l += (1 - l) * (pct / 100)
    return colorsys.hls_to_rgb(h, l, s)


def random_color():
    return colorsys.hls_to_rgb(
        random.choice(range(36))/36,
        random.choice(range(3, 9))/10,
        random.choice(range(6, 11))/10,
    )


# Some classic tile colors.
# More ideas: http://casaceramica.com/wp-content/gallery/moroccan-field-tiles/zellige-color-palette-wnames-sol.jpg
TILE_COLORS = [
    lighten(color255(45, 86, 72), 25),
    lighten(color255(38, 68, 111), 25),
    (1, 0, 0),
]
