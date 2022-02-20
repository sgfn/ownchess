from abc import ABC, abstractmethod

import pygame as pgm


class Sprite(ABC):
    """Abstract Base Class defining the sprite interface."""

    def __init__(self, ownchess_instance) -> None:
        """Initialise the sprite."""

        self.screen = ownchess_instance.screen
        self.settings = ownchess_instance.settings
        self.screen_rect = ownchess_instance.screen.get_rect()

    @abstractmethod
    def blitme(self) -> None:
        """Draw the sprite."""

        raise NotImplementedError()


class BoardSprite(Sprite):
    """Class for handling the board sprite."""

    def __init__(self, ownchess_instance, clr_light, clr_dark,
                 clr_highlight) -> None:
        """Initialise the board sprite and set its position."""

        super().__init__(ownchess_instance)

        self.colour_light = clr_light
        self.colour_dark = clr_dark
        self.colour_highlight = clr_highlight

        self.highlit_squares = []

        self.rects_small = [pgm.Rect((i//4 % 2*100)+(i % 4+1)*200, (i//4)*100,
                            100, 100) for i in range(32)]
        self.rect_big = pgm.Rect(200, 0, 800, 800)

    def blitme(self) -> None:
        """Draw the board."""

        pgm.draw.rect(self.screen, self.colour_dark, self.rect_big)
        for rect in self.rects_small:
            pgm.draw.rect(self.screen, self.colour_light, rect)
        for rect in self.highlit_squares:
            # pgm.draw.rect(self.screen, '#00000000', rect)
            pgm.draw.circle(self.screen, self.colour_highlight, rect.center, 25)


    def update_highlit_squares(self, highlit_squares):
        """"""

        self.highlit_squares = [pgm.Rect(col*100+200, row*100, 100, 100)
                                for row, col in highlit_squares]
        

class PieceSprite(Sprite):
    """Class for handling the piece sprite."""

    C_DICT = {
        'w': 'white',
        'b': 'black'
    }
    T_DICT = {
        'p': 'pawn',
        'b': 'bishop',
        'n': 'knight',
        'r': 'rook',
        'q': 'queen',
        'k': 'king'
    }

    def __init__(self, ownchess_instance, clr, type, coords_tpl) -> None:
        """Initialise the piece sprite and set its starting position."""

        super().__init__(ownchess_instance)

        img = f'images/{PieceSprite.T_DICT[type]}_{PieceSprite.C_DICT[clr]}.bmp'

        # Load the sprite's image and get its rect.
        self.image = pgm.image.load(img)
        self.rect = self.image.get_rect()

        self.row, self.col = coords_tpl

        # Set the position of the sprite
        self.rect.left = coords_tpl[1]*100 + 200
        self.rect.top = coords_tpl[0]*100

    def blitme(self) -> None:
        """Draw the sprite at its current location."""

        self.screen.blit(self.image, self.rect)


class TextSprite(Sprite):
    """Class for handling and rendering text."""

    def __init__(self, ownchess_instance, string, clr, left, top) -> None:
        """Initialise the text sprite and set its starting position."""
        super().__init__(ownchess_instance)

        self.rect = pgm.Rect(left, top, 0, 0)
        self.font = pgm.font.SysFont('Arial Black', 12)

        self.image = self.font.render(string, True, clr)

    def blitme(self) -> None:

        self.screen.blit(self.image, self.rect)
