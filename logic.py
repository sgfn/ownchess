from typing import Tuple


COL_ESC = '\x1b[0m'
COL_LIGHT_B = '\x1b[0;30;46m'
COL_LIGHT_W = '\x1b[0;37;46m'
COL_DARK_B = '\x1b[0;30;44m'
COL_DARK_W = '\x1b[0;37;44m'


class Piece:
    def __init__(self, colour: str, type: str) -> None:
        self.colour = colour
        self.type = type

    def __str__(self) -> str:
        return self.type.capitalize() if self.colour == 'w' else self.type


class Board:
    #   BOARD SETUP:
    #              C O L U M N S
    #      0   1   2   3   4   5   6   7
    #    8                                 0
    #    7                                 1
    #  r 6     B6=[2][1]                   2  R
    #  a 5                                 3  O
    #  n 4         C4=[4][2]               4  W
    #  k 3                                 5  S
    #  s 2                                 6
    #    1                                 7
    #      A   B   C   D   E   F   G   H
    #               f i l e s

    def __init__(self) -> None:
        """
        Creates a board object with an empty board.
        Use .setup() to prepare it for a game.
        """
        self.board = [[None for _ in range(8)] for _ in range(8)]

    def __str__(self) -> str:
        """Prints the board."""

        b_data = ""
        row_num = 8
        field_light = True
        for row in self.board:
            for field in row:
                if field_light:
                    if field is not None:
                        if field.colour == 'w':
                            b_data += COL_LIGHT_W + str(field)
                        else:
                            b_data += COL_LIGHT_B + str(field)
                    else:
                        b_data += COL_LIGHT_W + ' '
                else:
                    if field is not None:
                        if field.colour == 'w':
                            b_data += COL_DARK_W + str(field)
                        else:
                            b_data += COL_DARK_B + str(field)
                    else:
                        b_data += COL_DARK_W + ' '

                b_data += ' ' + COL_ESC
                field_light = not field_light
            b_data += str(row_num) + '\n'
            row_num -= 1
            field_light = not field_light
        b_data += ' A B C D E F G H'
        return b_data

    def __repr__(self) -> str:
        """
        Tells Python to always use the .__str__() method for printing the board.
        """
        return self.__str__()

    def setup(self) -> None:
        """Clears the board and prepares it for a new game."""

        data = ('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r')
        for i in range(8):
            self.board[0][i] = Piece('b', data[i])
            self.board[1][i] = Piece('b', 'p')
            self.board[6][i] = Piece('w', 'p')
            self.board[7][i] = Piece('w', data[i])
        for i in range(2, 6):
            self.board[i] = [None for _ in range(8)]

    def alg_to_own(self, alg_str: str) -> Tuple[int, int]:
        """
        Converts algebraic field coordinates to numerical ones 
        used by the board. Assumes the input is correct.
        """
        files = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        own_tpl = (8-int(alg_str[1]), files[alg_str[0].lower()])
        return own_tpl

    def move_piece(self, from_str: str, to_str: str = '') -> None:
        """
        Moves a single piece on the board (algebraic coordinates). 
        Will handle two 2-character strings or one 4-character string.
        Assumes the input is correct.
        """
        if not to_str:
            to_str = from_str[2:]
            from_str = from_str[:2]

        from_row, from_col = self.alg_to_own(from_str)
        to_row, to_col = self.alg_to_own(to_str)
        if self.board[from_row][from_col] is None:
            print('DEBUG: Nothing to move')
            return None
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None

    def mv(self, *args):
        """Alias for the .move_piece() method."""

        return self.move_piece(*args)

    def add_piece(self, colour: str, type: str,
                  coords: Tuple[int, int]) -> None:
        """
        Adds a piece to the board at the specified coordinates (own).
        Assumes the input is correct.
        """
        row, col = coords
        if self.board[row][col] is not None:
            print('DEBUG: Field occupied')
        self.board[row][col] = Piece(colour, type)

    def remove_piece(self, coords: Tuple[int, int]) -> None:
        """
        Removes a piece from the specified coordinates (own).
        Assumes the input is correct.
        """
        row, col = coords
        if self.board[row][col] is None:
            print('DEBUG: Nothing to remove')
        self.board[row][col] = None

    def move_is_legal(self, player_colour, from_tpl, to_tpl) -> int:
        """
        Checks whether a given move is legal. Might require refactoring later.
        Right now checks only if a piece moves the way it's supposed to
        (doesn't check for check(mate)s, pins etc.).
        """

        # Check whether the fields aren't the same
        if from_tpl == to_tpl:
            print('DEBUG: Not a move')
            return 1

        from_row, from_col = from_tpl
        to_row, to_col = to_tpl
        move_row = to_row - from_row
        move_col = to_col - from_col

        piece = self.board[from_row][from_col]
        dest = self.board[to_row][to_col]

        # Check whether the field is empty
        if piece is None:
            print('DEBUG: Nothing to move')
            return 2

        # Check whether one owns the piece
        if piece.colour != player_colour:
            print('DEBUG: Not your piece')
            return 3

        # Check whether the destination field isn't occupied by a friendly piece
        if dest is not None and dest.colour == player_colour:
            print('DEBUG: Target square occupied by a friendly piece')
            return 4

        if piece.type == 'k':
            return -1 <= move_row <= 1 and -1 <= move_col <= 1

        if piece.type == 'q':
            if move_row == 0:
                step_col = -1 if move_col < 0 else 1
                curr_col = from_col + step_col
                while curr_col != to_col:
                    if self.board[to_row][curr_col] is not None:
                        print('DEBUG: Another piece in the way')
                        return 5
                    curr_col += step_col
                return 0

            elif move_col == 0:
                step_row = -1 if move_row < 0 else 1
                curr_row = from_row + step_row
                while curr_row != to_row:
                    if self.board[curr_row][to_col] is not None:
                        print('DEBUG: Another piece in the way')
                        return 5
                    curr_row += step_row
                return 0

            elif abs(move_row) == abs(move_col):
                step_col = -1 if move_col < 0 else 1
                step_row = -1 if move_row < 0 else 1
                curr_col = from_col + step_col
                curr_row = from_row + step_row
                while curr_col != to_col:
                    if self.board[curr_row][curr_col] is not None:
                        print('DEBUG: Another piece in the way')
                        return 5
                    curr_row += step_row
                    curr_col += step_col
                return 0
            print('DEBUG: Not a valid move')
            return 6

        if piece.type == 'r':
            return move_row == 0 or move_col == 0

        if piece.type == 'b':
            return abs(move_row) == abs(move_col)

        if piece.type == 'n':
            return (move_row, move_col) in ((1, 2), (1, -2), (-1, 2), (-1, -2),
                                             (2, 1), (2, -1), (-2, 1), (-2, -1))
        
        # pawn
    
    def mil(self, colour, from_str, to_str=''):
        # Alias for the .move_is_legal() method utilising algebraic notation.
        if not to_str:
            to_str = from_str[2:]
            from_str = from_str[:2]

        from_tpl = self.alg_to_own(from_str)
        to_tpl = self.alg_to_own(to_str)

        return self.move_is_legal(colour, from_tpl, to_tpl)

class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.board.setup()
        self.to_move = 'w'
        self.b = self.board  # Alias for the board.


if __name__ == '__main__':
    gm = Game()
    print(gm.board)
