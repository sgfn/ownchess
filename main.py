import sys
from time import sleep

import pygame as pgm

from modules.sprites import BoardSprite, PieceSprite, TextSprite
from modules.board_old import Board
from modules.settings import Settings


class OwnchessGUI:
    """Overall class to manage program assets and behaviour."""

    def __init__(self):
        """
        Initialise the main instance of ownchess-gui and create its resources.
        """
        # Initialise the Pygame module and create the necessary objects
        pgm.init()
        self.settings = Settings()
        self.board = Board()

        # Create a screen object, the Pygame window
        self.screen = pgm.display.set_mode((self.settings.scr_width,
                                            self.settings.scr_height))

        # Set the window title
        pgm.display.set_caption("ownchess-gui")

        # Set the icon
        self.icon = pgm.image.load('images/icon.bmp')
        pgm.display.set_icon(self.icon)

        # Prepare the board
        test_fen_1 = '8/bRp2k2/2PNn3/3b4/8/1Q6/4K3/6r1 b - - 0 1'
        self._setup_position()

    def run_program(self):
        """Start the main loop of the program."""

        while True:
            # Check and handle new events
            self._check_events()

            self._update_screen()
            # Run at ~30 FPS so as not to use too many resources
            sleep(0.03)

    def _check_events(self) -> None:
        """Respond to keypresses and mouse events."""

        for event in pgm.event.get():
            # Close the window and quit when asked to
            if event.type == pgm.QUIT:
                sys.exit()
            # Handle mouse button presses and releases
            elif event.type == pgm.MOUSEBUTTONDOWN:
                mouse_pos = pgm.mouse.get_pos()
                self._check_mousebuttondown_events(event, mouse_pos)
            elif event.type == pgm.MOUSEBUTTONUP:
                self._check_mousebuttonup_events(event)

    def _check_mousebuttondown_events(self, event, mouse_pos):
        """Respond to mouse button presses."""
        for p_spr in self.piecesprites:
            if p_spr.rect.collidepoint(mouse_pos):
                self.boardsprite.update_highlit_squares(
                    self.board.get_legal_moves('', p_spr.row, p_spr.col))
                return None
        self.boardsprite.update_highlit_squares([])

    def _check_mousebuttonup_events(self, event):
        """Respond to mouse button releases."""
        
        pass

    def _setup_position(self, fen_str: str = '') -> None:
        """
        Prepare the board for playing, from FEN or default if no FEN specified.
        """
        self.board.setup(fen_str) if fen_str else self.board.setup()

        # Create sprites for the board and rank/file markers
        self.boardsprite = BoardSprite(self, self.settings.vis_sq_light_clr,
                                       self.settings.vis_sq_dark_clr,
                                       self.settings.vis_sq_highlight_clr)

        self.textsprites = []
        for i in range(8):
            self.textsprites.extend((
                TextSprite(
                    self, chr(97+i), self.settings.vis_sq_light_clr
                    if i % 2 == 0 else self.settings.vis_sq_dark_clr,
                    203+100*i, 782
                ),
                TextSprite(
                    self, str(i+1), self.settings.vis_sq_light_clr
                    if i % 2 == 1 else self.settings.vis_sq_dark_clr,
                    989, 700-100*i
                )
            ))

        # Create sprites for the pieces
        self.piecesprites = []
        for i in range(64):
            piece = self.board._chessboard[i//8][i % 8]
            if piece is not None:
                self.piecesprites.append(
                    PieceSprite(self, piece.colour, piece.type, (i//8, i % 8))
                )

    def _update_screen(self) -> None:
        """Update and draw everything on the screen, and flip to the new one."""

        # Fill the screen with the desired colour
        self.screen.fill(self.settings.vis_bg_clr)
        # Draw the board
        self.boardsprite.blitme()
        # Render the rank/file markers
        [obj.blitme() for obj in self.textsprites]
        # Draw the pieces
        [obj.blitme() for obj in self.piecesprites]
        # Refresh the screen to the new one
        pgm.display.flip()


if __name__ == '__main__':
    # Make a program instance, and run it.
    ownchess = OwnchessGUI()
    ownchess.run_program()
