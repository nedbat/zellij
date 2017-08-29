from zellij.design.base import P6mDesign
from zellij.euclid import Line


class CardsDesign(P6mDesign):
    description = "A tiling from Real Alcázar de Sevilla."

    def draw_tile(self, dwg):
        self.three_points()
        border_side = Line(self.top, self.bottom)

        with dwg.saved():
            dwg.reflect_line(self.top, self.belly)
            other_bottom = dwg.in_device(*self.bottom)
        other_bottom = dwg.in_user(*other_bottom)
        other_bottom_extent = border_side.parallel(other_bottom)

        offset = self.tilew * .15

        short_card = border_side.offset(-offset)
        belly_perp = border_side.perpendicular(self.belly)
        long_card = belly_perp.offset(offset)

        other_border_side = Line(self.top, other_bottom)
        short_middle = short_card.intersect(other_border_side)
        long_middle = long_card.intersect(other_bottom_extent)
        card_corner = short_card.intersect(long_card)

        dwg.move_to(*short_middle)
        dwg.line_to(*card_corner)
        dwg.line_to(*long_middle)
