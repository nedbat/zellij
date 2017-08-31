"""
Color support for Zellij.
"""

import colorsys
import random

import webcolors


def rgb255(r, g, b):
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
        random.choice(range(3, 7))/10,
        random.choice(range(6, 11))/10,
    )


def parse_color(s):
    """Parse a string, and return a color.

    As a special case, "none" returns an empty tuple ().

    The color is a tuple of floats 0..1
    """
    if s.lower() == "none":
        return ()

    try:
        return rgb255(*webcolors.name_to_rgb(s))
    except ValueError:
        try:
            return rgb255(*webcolors.hex_to_rgb(s))
        except ValueError:
            return "foo"


# Some classic tile colors.
# More ideas:
# https://s-media-cache-ak0.pinimg.com/736x/4c/4a/7b/4c4a7bfe6a545875ac26043d2371702f--kitchen-tiles-kitchen-colors.jpg
# http://www.sainttropezboutique.us/products/tiles/zillij-tiles-color-pallet.aspx

TILE_COLORS = [
    lighten(rgb255(45, 86, 72), 25),
    lighten(rgb255(38, 68, 111), 25),
    (1, 0, 0),
]

# From:
# http://casaceramica.com/wp-content/gallery/moroccan-field-tiles/zellige-color-palette-wnames-sol.jpg
# Also: zellige-color-palette-wnames-sol.xcf
class CasaCeramica:
    DarkGreen = rgb255(69, 110, 78)
    LightGreen = rgb255(151, 199, 189)
    DarkParsley = rgb255(120, 170, 111)
    Parsley = rgb255(152, 176, 94)
    AppleGreen = rgb255(188, 183, 108)
    AquaGreen = rgb255(135, 181, 179)
    Celadon = rgb255(189, 192, 186)
    NavyBlue = rgb255(36, 42, 101)
    LavenderBlue = rgb255(109, 145, 203)
    Turquoise = rgb255(83, 176, 221)
    LightTurquoise = rgb255(149, 197, 220)
    SkyBlue = rgb255(154, 175, 206)
    IceBlue = rgb255(183, 190, 203)
    Lava = rgb255(205, 171, 132)
    CharcoalGrey = rgb255(45, 44, 48)
    PearlGrey = rgb255(122, 127, 142)
    GreyChine = rgb255(199, 199, 202)
    Silver = rgb255(190, 188, 193)
    WhiteCarrare = rgb255(222, 221, 226)
    White = rgb255(209, 208, 211)
    Natural = rgb255(205, 178, 158)
    Black = rgb255(21, 20, 18)
    Chocolate = rgb255(33, 21, 18)
    Brown = rgb255(104, 31, 15)
    Honey = rgb255(180, 92, 27)
    Salmon = rgb255(185, 111, 55)
    Yellow = rgb255(221, 185, 87)
    Coral = rgb255(211, 138, 34)
    Red = rgb255(122, 30, 27)
    Peach = rgb255(179, 87, 79)
    Purple = rgb255(153, 85, 134)
    Pink = rgb255(204, 163, 176)
    Gold = rgb255(175, 134, 84)
