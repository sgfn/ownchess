from typing import Tuple, List


class Piece:
    def __init__(self, colour: str, type: str) -> None:
        self.colour = colour
        self.type = type

    def __str__(self) -> str:
        return self.type.capitalize() if self.colour == 'w' else self.type


class Board:
    """Class representing an 8x8 chessboard."""

    # Colour definitions for printing the board to stdout
    # Escape sequence
    CLR_ESC = '\x1b[0m'
    # Light squares
    CLR_L_B = '\x1b[0;30;46m'
    CLR_L_W = '\x1b[0;37;46m'
    # Dark squares
    CLR_D_B = '\x1b[0;30;44m'
    CLR_D_W = '\x1b[0;37;44m'
    # Highlit squares
    CLR_H_B = '\x1b[0;30;45m'
    CLR_H_W = '\x1b[0;37;45m'

    # Board coordinates:
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
        Creates a Board object with an empty 8x8 chessboard.
        Use setup() to prepare it for a game.
        """
        self.board = [[None for _ in range(8)] for _ in range(8)]

    def __str__(self, highlit_squares=set()) -> str:
        """
        Returns a string for printing the board (White's perspective) to stdout.
        Will highlight certain squares if passed a set of them as an argument.
        """
        s = ""
        sq_light = True  # (0, 0) is a light square
        for sq_row, row in enumerate(self.board):
            for sq_col, sq in enumerate(row):
                # Colour selection
                if (sq_row, sq_col) in highlit_squares:
                    clr = self.CLR_H_W if (sq is not None and
                                           sq.colour == 'w') else self.CLR_H_B
                elif sq_light:
                    clr = self.CLR_L_W if (sq is not None and
                                           sq.colour == 'w') else self.CLR_L_B
                else:
                    clr = self.CLR_D_W if (sq is not None and
                                           sq.colour == 'w') else self.CLR_D_B

                # If square occupied by a piece, print a corresponding letter
                if sq is not None:
                    sq_str = str(sq)
                else:
                    sq_str = ' '

                s += clr + sq_str + ' ' + self.CLR_ESC
                sq_light = not sq_light

            # Rank markings
            s += str(8 - sq_row) + '\n'
            sq_light = not sq_light

        # File markings
        s += ' A B C D E F G H'
        return s

    def __repr__(self, *args) -> str:
        """Links to __str__() as some printing functions call __repr__()."""

        return self.__str__(*args)

    def setup(self) -> None:
        """Sets the board up for a game."""

        initial = ('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r')
        for ind, el in enumerate(initial):
            self.board[0][ind] = Piece('b', el)
            self.board[1][ind] = Piece('b', 'p')
            self.board[6][ind] = Piece('w', 'p')
            self.board[7][ind] = Piece('w', el)
        for i in range(2, 6):
            self.board[i] = [None for _ in range(8)]

    def alg_to_num(self, coords_str: str) -> Tuple[int, int]:
        """
        Converts algebraic coordinates of a single square to numerical ones 
        used by the board. Raises ValueError for invalid strings.
        """

        if len(coords_str) != 2:
            raise ValueError(f'Unrecognised coordinates: {coords_str}')

        rank, file_ord = int(coords_str[1]), ord(coords_str[0].lower())

        # rank 'a' -> row 0, ord('a') = 97, thus ord(rank) must be in [97,97+7]
        if not 97 <= file_ord <= 104 or not 1 <= rank <= 8:
            raise ValueError(f'Invalid coordinates: {coords_str}')

        return (8 - rank, file_ord - 97)

    def move_piece(self, from_str: str, to_str: str = '') -> None:
        """
        Moves a single piece on the board (algebraic coordinates). 
        Will handle two 2-character strings or one 4-character string.
        """
        if to_str == '':
            to_str = from_str[2:]
            from_str = from_str[:2]

        from_row, from_col = self.alg_to_num(from_str)
        to_row, to_col = self.alg_to_num(to_str)

        if self.board[from_row][from_col] is None:
            print(f'DEBUG: Square {from_str} is empty')
            return None

        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None

    def mv(self, *args):
        """Alias for the move_piece() method."""

        return self.move_piece(*args)

    def add_piece(self, colour: str, type: str = '',
                  coords_str: str = '') -> None:
        """
        Adds a piece to the board at the specified coordinates (algebraic).
        Will handle three separate strings or one 4-character string.
        Syntax: add_piece("{colour}{type}{algebraic coords}")
        """
        if type == '':
            coords_str = colour[2:]
            type = colour[1]
            colour = colour[0]

        if colour not in ('w', 'b'):
            raise ValueError(f'Invalid piece colour: {colour}')
        if type not in ('p', 'b', 'n', 'r', 'q', 'k'):
            raise ValueError(f'Invalid piece type: {type}')

        row, col = self.alg_to_num(coords_str)

        if self.board[row][col] is not None:
            print(f'DEBUG: Square {coords_str} is occupied, replacing')

        self.board[row][col] = Piece(colour, type)

    def ad(self, *args):
        """Alias for the add_piece() method."""

        return self.add_piece(*args)

    def remove_piece(self, coords_str: str) -> None:
        """Removes a piece from the specified coordinates (algebraic)."""

        row, col = self.alg_to_num(coords_str)

        if self.board[row][col] is None:
            print(f'DEBUG: Square {coords_str} is empty')

        self.board[row][col] = None

    def rm(self, *args):
        """Alias for remove_piece()."""

        return self.remove_piece(*args)

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

        from_tpl = self.alg_to_num(from_str)
        to_tpl = self.alg_to_num(to_str)

        return self.move_is_legal(colour, from_tpl, to_tpl)

    def get_legal_moves(self, coords_str: str, sq_row=None, 
                        sq_col=None) -> List[Tuple[int, int]]:
        """
        Returns a list of legal moves.
        Does not take checks into account.
        Castling, en passant TBA.
        """
        if sq_row is None:
            sq_row, sq_col = self.alg_to_num(coords_str)
        piece = self.board[sq_row][sq_col]
        legal_moves = []
        all_moves = []

        if piece is None:
            print(f'DEBUG: No piece at {coords_str}')
            return legal_moves

        if piece.type == 'p':
            if piece.colour == 'w':
                all_moves.append((-1, 0))
                if sq_row == 6:
                    all_moves.append((-2, 0))
                all_captures = [(-1, -1), (-1, 1)]
            else:
                all_moves.append((1, 0))
                if sq_row == 1:
                    all_moves.append((2, 0))
                all_captures = [(1, -1), (1, 1)]

            first_field_empty = False
            for mv_row, mv_col in all_moves:
                if (0 <= sq_row + mv_row <= 7 and
                        0 <= sq_col + mv_col <= 7):
                    dest = self.board[sq_row+mv_row][sq_col+mv_col]
                    if dest is None:
                        if abs(mv_row) == 1:
                            first_field_empty = True
                            legal_moves.append((mv_row, mv_col))
                        else:
                            if first_field_empty:
                                legal_moves.append((mv_row, mv_col))

            for mv_row, mv_col in all_captures:
                if (0 <= sq_row + mv_row <= 7 and
                        0 <= sq_col + mv_col <= 7):
                    dest = self.board[sq_row+mv_row][sq_col+mv_col]
                    if dest is not None and dest.colour != piece.colour:
                        legal_moves.append((mv_row, mv_col))
            
            legal_moves = [(move_row+sq_row, move_col+sq_col) 
                           for move_row, move_col in legal_moves]
            return legal_moves

        if piece.type in ('k', 'n'):
            if piece.type == 'k':
                all_moves = [(1, 1), (1, 0), (1, -1), (0, 1),
                             (0, -1), (-1, 1), (-1, 0), (-1, -1)]
            else:
                all_moves = [(1, 2), (1, -2), (-1, 2), (-1, -2),
                             (2, 1), (2, -1), (-2, 1), (-2, -1)]

            for mv_row, mv_col in all_moves:
                if (0 <= sq_row + mv_row <= 7 and
                        0 <= sq_col + mv_col <= 7):
                    dest = self.board[sq_row+mv_row][sq_col+mv_col]
                    if dest is None or dest.colour != piece.colour:
                        legal_moves.append((mv_row, mv_col))
            
            legal_moves = [(move_row+sq_row, move_col+sq_col) 
                           for move_row, move_col in legal_moves]
            return legal_moves

        if piece.type in ('b', 'q'):
            all_moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        if piece.type in ('r', 'q'):
            all_moves.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])

        for mv_row, mv_col in all_moves:
            step_row, step_col = mv_row, mv_col
            found_piece = False
            while (0 <= sq_row + mv_row <= 7 and
                    0 <= sq_col + mv_col <= 7 and not found_piece):
                dest = self.board[sq_row+mv_row][sq_col+mv_col]
                if dest is None:
                    legal_moves.append((mv_row, mv_col))
                else:
                    found_piece = True
                    if dest.colour != piece.colour:
                        legal_moves.append((mv_row, mv_col))
                mv_row += step_row
                mv_col += step_col
        
        legal_moves = [(move_row+sq_row, move_col+sq_col) 
                       for move_row, move_col in legal_moves]
        return legal_moves

    def show_legal_moves(self, coords_str: str):
        """Prints the output of get_legal_moves() to stdout."""

        # field_row, field_col = self.alg_to_num(coords_str)
        legal_moves = self.get_legal_moves(coords_str)

        highlit_squares = set(legal_moves)

        print(self.__str__(highlit_squares=highlit_squares))

    def slm(self, *args):
        """Alias for show_legal_moves()."""

        return self.show_legal_moves(*args)


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
    # gm = Game()
    # while True:
    #     print(gm.board)
    #     gm.ply(input())
    b = Board()
    active = True
    while active:
        cmd, *args = input().split()
        if cmd == 'q':
            active = False
        elif cmd == 'b':
            print(b)
        elif cmd in ('ad', 'a'):
            b.ad(*args)
        elif cmd in ('rm', 'r'):
            b.rm(*args)
        elif cmd in ('mv', 'm'):
            b.mv(*args)
        elif cmd in ('slm', 's'):
            b.slm(*args)
        else:
            print('DEBUG: Unknown command')
