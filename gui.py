import pygame as pgm


class BoardSprite:
    """Class with all necessary methods for handling a sprite."""

    def __init__(self, ownchess_instance) -> None:
        """Initialise the board."""

        self.screen = ownchess_instance.screen
        self.settings = ownchess_instance.settings
        self.screen_rect = ownchess_instance.screen.get_rect()

        self.colour_light = '#DDDDDD'
        self.colour_dark = '#555555'

        self.rects_small = [pgm.Rect((i//4 % 2*100)+(i % 4+1)*200, (i//4)*100,
                            100, 100) for i in range(32)]
        self.rect_big = pgm.Rect(200, 0, 800, 800)

    def blitme(self):
        """Draw the board."""

        pgm.draw.rect(self.screen, self.colour_dark, self.rect_big)
        for rect in self.rects_small:
            pgm.draw.rect(self.screen, self.colour_light, rect)


class PieceSprite:

    colours = {
        'w': 'white',
        'b': 'black'
    }
    types = {
        'p': 'pawn',
        'b': 'bishop',
        'n': 'knight',
        'r': 'rook',
        'q': 'queen',
        'k': 'king'
    }

    def __init__(self, ownchess_instance, colour, type, coords_tpl) -> None:
        """Initialise the piece sprite and set its starting position."""

        self.screen = ownchess_instance.screen
        self.settings = ownchess_instance.settings
        self.screen_rect = ownchess_instance.screen.get_rect()

        imgpath = f'images/{PieceSprite.types[type]}_{PieceSprite.colours[colour]}.bmp'

        # Load the sprite's image and get its rect.
        self.image = pgm.image.load(imgpath)
        self.rect = self.image.get_rect()

        # Set the position of the sprite
        self.rect.left = coords_tpl[1]*100 + 200
        self.rect.top = coords_tpl[0]*100

    def blitme(self):
        """Draw the sprite at its current location."""
        self.screen.blit(self.image, self.rect)
