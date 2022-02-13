from typing import Tuple
from unittest import TestResult


COLOUR_ESC = '\x1b[0m'
COLOUR_LIGHT_B = '\x1b[0;30;46m'
COLOUR_LIGHT_W = '\x1b[0;37;46m'
COLOUR_DARK_B = '\x1b[0;30;44m'
COLOUR_DARK_W = '\x1b[0;37;44m'
COLOUR_HIGHLIGHT_B = '\x1b[0;30;41m'
COLOUR_HIGHLIGHT_W = '\x1b[0;37;41m'


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
                            b_data += COLOUR_LIGHT_W + str(field)
                        else:
                            b_data += COLOUR_LIGHT_B + str(field)
                    else:
                        b_data += COLOUR_LIGHT_W + ' '
                else:
                    if field is not None:
                        if field.colour == 'w':
                            b_data += COLOUR_DARK_W + str(field)
                        else:
                            b_data += COLOUR_DARK_B + str(field)
                    else:
                        b_data += COLOUR_DARK_W + ' '

                b_data += ' ' + COLOUR_ESC
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

        def signum(val: int) -> int:
            """Helper function for getting the step value."""

            if val == 0:
                return 0
            return 1 if val > 0 else -1

        def collision_checker(b, fr_r, fr_c, to_r, to_c):
            """Helper function for detecting collisions with other pieces."""

            st_r = signum(to_r - fr_r)
            st_c = signum(to_c - fr_c)
            curr_r = fr_r + st_r
            curr_c = fr_c + st_c

            while curr_c != to_c or curr_r != to_r:
                if b[curr_r][curr_c] is not None:
                    return False
                curr_c += st_c
                curr_r += st_r

            return True

        # Check whether the fields aren't the same
        if from_tpl == to_tpl:
            print('DEBUG: Not a move')
            return 1

        fr_r, fr_c = from_tpl
        to_r, to_c = to_tpl
        mv_r = to_r - fr_r
        mv_c = to_c - fr_c

        piece = self.board[fr_r][fr_c]
        dest = self.board[to_r][to_c]

        # Check whether the field is empty
        if piece is None:
            print('DEBUG: Nothing to move')
            return 2

        # Check whether one owns the piece
        if piece.colour != player_colour:
            print('DEBUG: Not your piece')
            return 3

        # Check whether the destination field is occupied by a friendly piece
        if dest is not None and dest.colour == player_colour:
            print('DEBUG: Target square occupied by a friendly piece')
            return 4

        if piece.type == 'k':
            if -1 <= mv_r <= 1 and -1 <= mv_c <= 1:
                return 0
            else:
                print('DEBUG: Not a valid move')
                return 6

        if piece.type == 'q':
            if mv_r == 0 or mv_c == 0 or abs(mv_r) == abs(mv_c):
                if collision_checker(self.board, fr_r, fr_c, to_r, to_c):
                    return 0
                else:
                    print('DEBUG: Another piece in the way')
                    return 5
            else:
                print('DEBUG: Not a valid move')
                return 6

        if piece.type == 'r':
            if mv_r == 0 or mv_c == 0:
                if collision_checker(self.board, fr_r, fr_c, to_r, to_c):
                    return 0
                else:
                    print('DEBUG: Another piece in the way')
                    return 5
            else:
                print('DEBUG: Not a valid move')
                return 6

        if piece.type == 'b':
            if abs(mv_r) == abs(mv_c):
                if collision_checker(self.board, fr_r, fr_c, to_r, to_c):
                    return 0
                else:
                    print('DEBUG: Another piece in the way')
                    return 5
            else:
                print('DEBUG: Not a valid move')
                return 6

        if piece.type == 'n':
            if (abs(mv_r), abs(mv_c)) in ((1, 2), (2, 1)):
                return 0
            else:
                print('DEBUG: Not a valid move')
                return 6

        # Piece is a pawn
        mv_pawn = -1 if piece.colour == 'w' else 1
        sr_pawn = 6 if piece.colour == 'w' else 1
        pr_pawn = 0 if piece.colour == 'w' else 7
        # Standard pawn move
        if mv_r == mv_pawn and mv_c == 0:
            if dest is not None and dest.colour != player_colour:
                print('DEBUG: Pawns capture diagonally')
                return 6
            return 0

        # First pawn move, advance by two ranks
        if fr_r == sr_pawn and mv_r == mv_pawn * 2 and mv_c == 0:
            if dest is not None and dest.colour != player_colour:
                print('DEBUG: Pawns capture diagonally')
                return 6

            if collision_checker(self.board, fr_r, fr_c, to_r, to_c):
                return 0
            else:
                print('DEBUG: Another piece in the way')
                return 5

        # Standard pawn capture
        if mv_r == mv_pawn and abs(mv_c) == 1:
            if dest is not None and dest.colour != player_colour:
                return 0
            print('DEBUG: Pawns can only move diagonally when capturing')
            return 6

        # En passant
        # TBI

        # Promotion
        if mv_r == mv_pawn and to_r == pr_pawn:
            if dest is not None and dest.colour != player_colour:
                print('DEBUG: Pawns capture diagonally')
                return 6
            # right now won't get called, will be handled by the first if

            pass

        print('DEBUG: Not a valid move')
        return 6

    def mil(self, colour, from_str, to_str=''):
        # Alias for the .move_is_legal() method utilising algebraic notation.
        if not to_str:
            to_str = from_str[2:]
            from_str = from_str[:2]

        from_tpl = self.alg_to_own(from_str)
        to_tpl = self.alg_to_own(to_str)

        return self.move_is_legal(colour, from_tpl, to_tpl)

    def get_legal_moves(self, field_str):
        """
        Function returning a list of legal moves.
        Does not take checks into account.
        Castling, en passant TBA.
        """
        field_row, field_col = self.alg_to_own(field_str)
        piece = self.board[field_row][field_col]
        legal_moves = []
        possible_moves = []

        if piece is None:
            print(f'DEBUG: No piece at {field_str.lower()}')
            return legal_moves

        if piece.type == 'p':
            if piece.colour == 'w':
                possible_moves.append((-1, 0))
                if field_row == 6:
                    possible_moves.append((-2, 0))
                possible_captures = [(-1, -1), (-1, 1)]
            else:
                possible_moves.append((1, 0))
                if field_row == 1:
                    possible_moves.append((2, 0))
                possible_captures = [(1, -1), (1, 1)]
            
            first_field_empty = False
            for move_row, move_col in possible_moves:
                if (0 <= field_row + move_row <= 7 and
                        0 <= field_col + move_col <= 7):
                    dest = self.board[field_row+move_row][field_col+move_col]
                    if dest is None:
                        if abs(move_row) == 1:
                            first_field_empty = True
                            legal_moves.append((move_row, move_col))
                        else:
                            if first_field_empty:
                                legal_moves.append((move_row, move_col))

            for move_row, move_col in possible_captures:
                if (0 <= field_row + move_row <= 7 and
                        0 <= field_col + move_col <= 7):
                    dest = self.board[field_row+move_row][field_col+move_col]
                    if dest is not None and dest.colour != piece.colour:
                        legal_moves.append((move_row, move_col))

            return legal_moves

        if piece.type == 'k':
            possible_moves = [(1, 1), (1, 0), (1, -1), (0, 1), 
                              (0, -1), (-1, 1), (-1, 0), (-1, -1)]

        if piece.type == 'n':
            possible_moves = [(1, 2), (1, -2), (-1, 2), (-1, -2),
                              (2, 1), (2, -1), (-2, 1), (-2, -1)]

        if piece.type in ('k', 'n'):              
            for move_row, move_col in possible_moves:
                if (0 <= field_row + move_row <= 7 and
                        0 <= field_col + move_col <= 7):
                    dest = self.board[field_row+move_row][field_col+move_col]
                    if dest is None or dest.colour != piece.colour:
                        legal_moves.append((move_row, move_col))
            return legal_moves

        if piece.type in ('b', 'q'):
            possible_moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        if piece.type in ('r', 'q'):
            possible_moves.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])

        for move_row, move_col in possible_moves:
            step_row, step_col = move_row, move_col
            found_piece = False
            while (0 <= field_row + move_row <= 7 and 
                    0 <= field_col + move_col <= 7 and not found_piece):
                dest = self.board[field_row+move_row][field_col+move_col]
                if dest is None:
                    legal_moves.append((move_row, move_col))
                else:
                    found_piece = True
                    if dest.colour != piece.colour:
                        legal_moves.append((move_row, move_col))
                move_row += step_row
                move_col += step_col
        return legal_moves

    def show_legal_moves(self, field_str):
        field_row, field_col = self.alg_to_own(field_str)
        legal_moves = self.get_legal_moves(field_str)
        highlit_fields = [(move_row + field_row, move_col + field_col) 
                            for move_row, move_col in legal_moves]
        # Modified copy of .__str__() method (ineffective)
        b_data = ""
        row_num = 8
        field_light = True
        for field_row, row in enumerate(self.board):
            for field_col, field in enumerate(row):
                if (field_row, field_col) in highlit_fields:
                    if field is not None:
                        if field.colour == 'w':
                            b_data += COLOUR_HIGHLIGHT_W + str(field)
                        else:
                            b_data += COLOUR_HIGHLIGHT_B + str(field)
                    else:
                        b_data += COLOUR_HIGHLIGHT_W + ' '
                elif field_light:
                    if field is not None:
                        if field.colour == 'w':
                            b_data += COLOUR_LIGHT_W + str(field)
                        else:
                            b_data += COLOUR_LIGHT_B + str(field)
                    else:
                        b_data += COLOUR_LIGHT_W + ' '
                else:
                    if field is not None:
                        if field.colour == 'w':
                            b_data += COLOUR_DARK_W + str(field)
                        else:
                            b_data += COLOUR_DARK_B + str(field)
                    else:
                        b_data += COLOUR_DARK_W + ' '

                b_data += ' ' + COLOUR_ESC
                field_light = not field_light
            b_data += str(row_num) + '\n'
            row_num -= 1
            field_light = not field_light
        b_data += ' A B C D E F G H'
        print(b_data)


class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.board.setup()
        self.to_move = 'w'
        self.b = self.board  # Alias for the board.

    def ply(self, move_str) -> None:
        if self.board.mil(self.to_move, move_str) == 0:
            self.board.move_piece(move_str)
            self.to_move = 'b' if self.to_move == 'w' else 'w'


if __name__ == '__main__':
    gm = Game()
    while True:
        print(gm.board)
        gm.ply(input())
