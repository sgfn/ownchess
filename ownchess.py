import sys

import pygame as pgm

from settings import Settings
from gui import BoardSprite, PieceSprite
from logic import Game, Board, Piece

class OwnchessGUI:
    """Overall class to manage program assets and behaviour."""

    def __init__(self):
        """
        Initialise the main instance of ownchess-gui and create its resources.
        """

        # Initialise the Pygame module
        pgm.init()
        self.settings = Settings()
        self.game = Game()
        self.board = self.game.board

        # Create a screen object, the Pygame window
        self.screen = pgm.display.set_mode((self.settings.screen_width, 
            self.settings.screen_height))
        
        self.testsprite = BoardSprite(self)
        self.piecesprites = [None for _ in range(32)]
        for i in range(8):
            for j, k in ((0, 0), (1, 1), (2, 6), (3, 7)):
                piece = self.board.board[k][i]
                self.piecesprites[j*8 + i] = PieceSprite(self, piece.colour, 
                                                         piece.type, (k, i))

        # Set the window title
        pgm.display.set_caption("ownchess-gui")
        
    def run_program(self):
        """Start the main loop for the program."""

        while True:
            # Keep checking and handling events which happened since the last 
            #   pass of the loop.
            for event in pgm.event.get():
                # Close the window and quit when asked to
                if event.type == pgm.QUIT:
                    sys.exit()
            # Draw everything on the screen
            # Fill the screen with the desired colour
            self.screen.fill(self.settings.visual_bg_colour)
            # Draw the test rect
            self.testsprite.blitme()
            # Draw the pieces
            for piece in self.piecesprites:
                piece.blitme()
            # Refresh the screen to the new one
            pgm.display.flip()

if __name__ == '__main__':
    # Make a program instance, and run it.
    ownchess = OwnchessGUI()
    ownchess.run_program()