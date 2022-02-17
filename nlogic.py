from typing import List


class Square:
    """Class representing a single square in the board."""

    def __init__(self) -> None:
        """Create an empty Square object with the necessary properties."""

        self._colour = 'e'
        self._piece = 'e'
    
    def set_sq(self, colour: str = 'e', piece: str = 'e') -> None:
        """Set the square to the desired piece."""

        self._colour = colour
        self._piece = piece
    
    def __str__(self) -> str:
        if self._colour == 'e':
            return ' '
        else:
            return self._piece.upper() if self._colour == 'w' else self._piece


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

    # Default FEN string
    FEN_DEF = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    # Board coordinates:
    #              C O L U M N S
    #           0   1   2   3   4   5   6   7
    #    8                                 63   7
    #    7                                      6
    #  r 6                                      5  R
    #  a 5                                      4  O
    #  n 4                                      3  W
    #  k 3                                      2  S - multiply by 8
    #  s 2      8   9  10  11   ...             1
    #    1      0   1   2   3   4   5   6   7   0
    #           A   B   C   D   E   F   G   H
    #               f i l e s

    def __init__(self) -> None:
        """
        Creates a Board object with an empty 8x8 chessboard.
        Use import_fen() to prepare it for a game.
        """
        self._chessboard = [Square() for _ in range(64)]

        # Create variables to hold board properties
        self._to_move = None
        self._can_castle = None
        self._ep_square = -1
        self._halfmove_clock = None
        self._fullmove_counter = None

        # # Create piece lists
        # self._white_pieces = []
        # self._black_pieces = []
        
        # # Create helper variables containing the king's positions
        # self._white_king_coords_tpl = None
        # self._black_king_coords_tpl = None

    def __str__(self, highlit_squares=set()) -> str:
        """
        Returns a string for printing the board (White's perspective) to stdout.
        Will highlight certain squares if passed a set of them as an argument.
        """
        s = ""
        sq_light = True  # 56 is a light square
        for sq_row in range(7, -1, -1):
            for sq_col in range(8):
                sq = self._chessboard[sq_row*8 + sq_col]
                # Colour selection
                if sq_row*8 + sq_col in highlit_squares:
                    clr = Board.CLR_H_W if sq._colour == 'w' else Board.CLR_H_B
                elif sq_light:
                    clr = Board.CLR_L_W if sq._colour == 'w' else Board.CLR_L_B
                else:
                    clr = Board.CLR_D_W if sq._colour == 'w' else Board.CLR_D_B

                s += clr + str(sq) + ' ' + Board.CLR_ESC
                sq_light = not sq_light

            # Rank markings
            s += str(sq_row + 1) + '\n'
            sq_light = not sq_light

        # File markings
        s += ' A B C D E F G H'
        return s

    def __repr__(self, *args) -> str:
        """Links to __str__() as some printing functions call __repr__()."""

        return self.__str__(*args)

    def import_fen(self, fen: str = '') -> None:
        """
        Set the board up for a game (from FEN).
        Does not check whether the FEN string is correct.
        """
        # Set default FEN if not specified
        if fen == '':
            fen = Board.FEN_DEF

        # Set the starting properties
        (rows, self._to_move, self._can_castle, self._ep_square, 
        self._halfmove_clock, self._fullmove_counter) = fen.strip().split(' ')
        
        # Create the pieces and insert them on the chessboard
        for f_row, row_str in enumerate(rows.split('/')):
            col = 0
            for char in row_str:
                # char is a number
                if 49 <= ord(char) <= 56:
                    col += int(char)

                # char is a piece
                else:
                    colour = 'b' if char.lower() == char else 'w'
                    piece = char.lower()
                        
                    self._chessboard[(7-f_row)*8 + col].set_sq(colour, piece)

                    col += 1
        
    def alg_to_num(self, coords_str: str) -> int:
        """
        Converts algebraic coordinates of a single square to numerical ones 
        used by the board.
        """

        rank, file_ord = int(coords_str[1]), ord(coords_str[0].lower())
        # file 'a' -> col 0, ord('a') = 97
        return (rank - 1) * 8 + (file_ord - 97)

    def move_piece(self, from_num: int, to_num: int = -1) -> None:
        """Moves/removes a single piece (numerical coordinates)."""

        from_sq = self._chessboard[from_num]

        if from_sq._colour == 'e':
            print(f'DEBUG: Square {from_num} is empty')
            return None

        if to_num != -1:
            self._chessboard[to_num].set_sq(from_sq._colour, from_sq._piece)

        from_sq.set_sq()

    def add_piece(self, colour: str, piece: str, sq_num: int) -> None:
        """Adds a piece at the specified coordinates (numerical)."""

        to_sq = self._chessboard[sq_num]
        if to_sq._colour != 'e':
            print(f'DEBUG: Square {sq_num} is occupied, replacing')

        to_sq.set_sq(colour, piece)

    def get_pseudolegal_moves(self, sq_num: int) -> List[int]:
        """
        Returns a list of squares available for pseudolegal moves.
        Does not take checks into account.
        Castling, en passant TBA.
        """
        
        from_sq = self._chessboard[sq_num]
        pseudolegal_moves = []
        all_moves = []

        if from_sq._colour == 'e':
            print(f'DEBUG: Square {sq_num} is empty')

        # Piece is a pawn
        elif from_sq._piece == 'p':
            start_row, pawn_move = (1, 8) if from_sq._colour == 'w' else (6, -8)
            
            # Standard move
            all_moves.append(pawn_move)
            # First pawn move
            if 8*start_row <= sq_num <= 8*start_row + 7:
                all_moves.append(2*pawn_move)
            # Pawn captures
            all_captures = [pawn_move - 1, pawn_move + 1]

            for mv_num in all_moves:
                dest_num = sq_num + mv_num
                # Checking this might be redundant
                if 0 <= dest_num <= 63:
                    to_sq = self._chessboard[dest_num]
                    # Cannot advance pawns onto occupied squares
                    if to_sq._colour != 'e':
                        break
                    # If square is empty, the pawn can be moved there
                    pseudolegal_moves.append(dest_num)

            for mv_num in all_captures:
                dest_num = sq_num + mv_num
                # See above
                if 0 <= dest_num <= 63:
                    to_sq = self._chessboard[dest_num]
                    # Standard pawn capture, en passant capture
                    if ((to_sq._colour not in ('e', from_sq._colour)) or 
                        (to_sq._colour == 'e' and self._ep_square == dest_num)):
                        pseudolegal_moves.append(dest_num)

            return pseudolegal_moves

        # Piece is a king or a knight (not a ray piece)
        elif from_sq._piece in ('k', 'n'):
            if from_sq._piece == 'k':
                all_moves = [-9, -8, -7, -1, 1, 7, 8, 9]
            else:
                # NOT A GOOD IDEA
                all_moves = [-17, -15, -10, -6, 6, 10, 15, 17]

            for mv_num in all_moves:
                dest_num = sq_num + mv_num
                if 0 <= dest_num <= 63:
                    to_sq = self._chessboard[dest_num]
                    if to_sq._colour != from_sq._colour:
                        pseudolegal_moves.append(dest_num)

            return pseudolegal_moves

        # Piece is a bishop, a rook or a queen (ray piece)
        else:
            if from_sq._piece in ('b', 'q'):
                all_moves = [-9, -7, 7, 9]
            if from_sq._piece in ('r', 'q'):
                all_moves.extend((-8, -1, 1, 8))

            for mv_num in all_moves:
                i = 1
                dest_num = sq_num + i*mv_num
                while 0 <= dest_num <= 63:
                    to_sq = self._chessboard[dest_num]
                    if to_sq._colour == 'e':
                        pseudolegal_moves.append(dest_num)
                    else:
                        if to_sq._colour != from_sq._colour:
                            pseudolegal_moves.append(dest_num)
                        break
                    i += 1
                    dest_num = sq_num + i*mv_num

        return pseudolegal_moves

    def show_pseudolegal_moves(self, sq_num: int) -> None:
        """Prints the output of get_pseudolegal_moves() to stdout."""

        pseudolegal_moves = self.get_pseudolegal_moves(sq_num)
        print(self.__str__(highlit_squares=set(pseudolegal_moves)))

    def is_in_check(self, player_colour: str = '') -> bool:
        """
        Test whether the specified player (default: next to move) is in check.
        """
        if player_colour == '':
            player_colour = self._to_move

        if player_colour == 'w':
            k_row, k_col = self._white_king_coords_tpl
        else:
            k_row, k_col = self._black_king_coords_tpl

        knight_fields = ((1, 2), (1, -2), (-1, 2), (-1, -2), 
                         (2, 1), (2, -1), (-2, 1), (-2, -1))
        
        for mv_row, mv_col in knight_fields:
            dest_row, dest_col = k_row + mv_row, k_col + mv_col
            if 0 <= dest_row <= 7 and 0 <= dest_col <= 7:
                piece = self._chessboard[dest_row][dest_col]
                if (piece is not None and piece.type == 'n' 
                    and piece.colour != player_colour):
                    return True
        

        

if __name__ == '__main__':
    board = Board()
    active = True
    while active:
        cmd, *args = input().split()
        if cmd == 'q':
            active = False
        elif cmd == 'b':
            print(board)
        elif cmd in ('ad', 'a'):
            board.add_piece(*args)
        elif cmd in ('mv', 'm'):
            board.move_piece(*args)
        elif cmd in ('slm', 's'):
            board.show_pseudolegal_moves(int(*args))
        elif cmd in ('ff', 'fen', 'f'):
            fen_str = ''
            for arg in args:
                fen_str += arg + ' '
            board.import_fen(fen_str) if fen_str != '' else board.import_fen()
        else:
            print('DEBUG: Unknown command')
