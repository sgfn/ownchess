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
        """Return the piece in FEN for displaying on the board."""

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
        self._to_move = '-'
        self._can_castle = '-'
        self._ep_square = -1
        self._halfmove_clock = -1
        self._fullmove_counter = -1

        # # Create piece lists
        # self._white_pieces = []
        # self._black_pieces = []
        
        # Create helper properties containing the king's positions
        self._w_king_sq = -1
        self._b_king_sq = -1

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

        # Clear the board
        for square in self._chessboard:
            square.set_sq()

        # Set the starting properties
        (rows, self._to_move, self._can_castle, ep_sq, hm_cl, 
        fm_ct) = fen.strip().split(' ')
        
        # Convert the values
        self._ep_square = self.alg_to_num(ep_sq)
        self._halfmove_clock = int(hm_cl)
        self._fullmove_counter = int(fm_ct)

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
                    sq_num = (7-f_row)*8 + col
                    if piece == 'k':
                        self._update_king(colour, sq_num)
                    self._chessboard[sq_num].set_sq(colour, piece)
                    col += 1
        
    def alg_to_num(self, coords_str: str) -> int:
        """
        Converts algebraic coordinates of a single square to numerical ones 
        used by the board.
        """
        if len(coords_str) != 2:
            return -1
        rank, file_ord = int(coords_str[1]), ord(coords_str[0].lower())
        # file 'a' -> col 0, ord('a') = 97
        return (rank - 1) * 8 + (file_ord - 97)

    def move_piece(self, from_num: int, to_num: int = -1, 
                   promote_to: str = 'q') -> int:
        """
        Moves/removes a single piece (numerical coordinates). Returns 1 (pawn 
        move), 2 (capture) if move resets the halfmove counter; 0 otherwise.
        """
        returnval = 0
        from_sq = self._chessboard[from_num]

        if from_sq._colour == 'e':
            print(f'DEBUG: Square {from_num} is empty')
            return None

        if from_sq._piece == 'k':
            self._update_king(from_sq._colour, to_num)
        # Not checking if target square contains a king, might be needed later

        if to_num != -1:
            if self._chessboard[to_num]._colour not in ('e', from_sq._colour):
                returnval = 2

        if from_sq._piece == 'p':
            # Handling promotions
            # DON'T WORK AS INTENDED RIGHT NOW
            pr_row = 7 if from_sq._colour == 'w' else 0
            if to_num // 8 == pr_row:
                self.add_piece(from_sq._colour, promote_to, to_num)
                to_num = -1
            
            # Handling en passant
            elif to_num == self._ep_square:
                if to_num > from_num:
                    self._chessboard[to_num - 8].set_sq()
                else:
                    self._chessboard[to_num + 8].set_sq()
            returnval = 1

        if to_num != -1:
            self._chessboard[to_num].set_sq(from_sq._colour, from_sq._piece)
        from_sq.set_sq()

        return returnval

    def add_piece(self, colour: str, piece: str, sq_num: int) -> None:
        """Adds a piece at the specified coordinates (numerical)."""

        to_sq = self._chessboard[sq_num]
        if to_sq._colour != 'e':
            print(f'DEBUG: Square {sq_num} is occupied, replacing')

        if piece == 'k':
            self._update_king(colour, sq_num)

        to_sq.set_sq(colour, piece)

    def get_pseudolegal_moves(self, sq_num: int) -> List[int]:
        """
        Returns a list of squares available for pseudolegal moves.
        Does not take checks into account.
        Castling TBA.
        """
        from_sq = self._chessboard[sq_num]
        from_row, from_col = sq_num // 8, sq_num % 8
        pseudolegal_moves = []
        all_moves = []

        if from_sq._colour == 'e':
            print(f'DEBUG: Square {sq_num} is empty')
        
        # Piece is a pawn
        elif from_sq._piece == 'p':
            start_row, pawn_move = (1, 1) if from_sq._colour == 'w' else (6, -1)
            # Standard move
            all_moves.append((pawn_move, 0))
            # First pawn move
            if from_row == start_row:
                all_moves.append((2*pawn_move, 0))
            # Pawn captures
            all_captures = [(pawn_move, -1), (pawn_move, 1)]

            for mv_row, mv_col in all_moves:
                dest_row, dest_col = from_row + mv_row, from_col + mv_col
                # Checking this might be redundant
                if 0 <= dest_row <= 7 and 0 <= dest_col <= 7:
                    dest_num = dest_row*8 + dest_col
                    to_sq = self._chessboard[dest_num]
                    # Cannot advance pawns onto occupied squares
                    if to_sq._colour != 'e':
                        break
                    # If square is empty, the pawn can be moved there
                    pseudolegal_moves.append(dest_num)

            for mv_row, mv_col in all_captures:
                dest_row, dest_col = from_row + mv_row, from_col + mv_col
                # See above
                if 0 <= dest_row <= 7 and 0 <= dest_col <= 7:
                    dest_num = dest_row*8 + dest_col
                    to_sq = self._chessboard[dest_num]
                    # Standard pawn capture, en passant capture
                    if ((to_sq._colour not in ('e', from_sq._colour)) or 
                        (to_sq._colour == 'e' and self._ep_square == dest_num)):
                        pseudolegal_moves.append(dest_num)

        # Piece is a king or a knight (not a ray piece)
        elif from_sq._piece in ('k', 'n'):
            if from_sq._piece == 'k':
                all_moves = [(1, 1), (1, 0), (1, -1), (0, 1),
                             (0, -1), (-1, 1), (-1, 0), (-1, -1)]
            else:
                all_moves = [(1, 2), (1, -2), (-1, 2), (-1, -2),
                             (2, 1), (2, -1), (-2, 1), (-2, -1)]

            for mv_row, mv_col in all_moves:
                dest_row, dest_col = from_row + mv_row, from_col + mv_col
                if 0 <= dest_row <= 7 and 0 <= dest_col <= 7:
                    dest_num = dest_row*8 + dest_col
                    to_sq = self._chessboard[dest_num]
                    if to_sq._colour != from_sq._colour:
                        pseudolegal_moves.append(dest_num)

        # Piece is a bishop, a rook or a queen (ray piece)
        else:
            if from_sq._piece in ('b', 'q'):
                all_moves = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            if from_sq._piece in ('r', 'q'):
                all_moves.extend(((-1, 0), (0, -1), (1, 0), (0, 1)))

            for mv_row, mv_col in all_moves:
                dest_row, dest_col = from_row + mv_row, from_col + mv_col
                while 0 <= dest_row <= 7 and 0 <= dest_col <= 7:
                    dest_num = dest_row*8 + dest_col
                    to_sq = self._chessboard[dest_num]
                    if to_sq._colour == 'e':
                        pseudolegal_moves.append(dest_num)
                    else:
                        if to_sq._colour != from_sq._colour:
                            pseudolegal_moves.append(dest_num)
                        break
                    dest_row += mv_row
                    dest_col += mv_col

        return pseudolegal_moves

    def show_legal_moves(self, sq_num: int) -> None:
        """Prints the output of get_legal_moves() to stdout."""
        legal_moves = self.get_legal_moves(sq_num)
        print(self.__str__(highlit_squares=set(legal_moves)))

    def is_in_check(self, king_colour: str = '') -> bool:
        """
        Test whether the specified player (default: next to move) is in check.
        """
        if king_colour == '':
            king_colour = self._to_move

        if king_colour == 'w':
            k_row, k_col = self._w_king_sq // 8, self._w_king_sq % 8
        else:
            k_row, k_col = self._b_king_sq // 8, self._b_king_sq % 8

        # Pawn checks
        pawn_move = 1 if king_colour == 'w' else -1
        pawn_moves = [(pawn_move, -1), (pawn_move, 1)]
        for mv_row, mv_col in pawn_moves:
            atk_row, atk_col = k_row + mv_row, k_col + mv_col
            if 0 <= atk_row <= 7 and 0 <= atk_col <= 7:
                atk_sq = self._chessboard[atk_row*8 + atk_col]
                if (atk_sq._colour != king_colour and atk_sq._piece == 'p'):
                    return True

        # "King checks" - illegal moves where both kings are on adjacent squares
        king_moves = [(1, 1), (1, 0), (1, -1), (0, 1),
                       (0, -1), (-1, 1), (-1, 0), (-1, -1)]
        for mv_row, mv_col in king_moves:
            atk_row, atk_col = k_row + mv_row, k_col + mv_col
            if 0 <= atk_row <= 7 and 0 <= atk_col <= 7:
                atk_sq = self._chessboard[atk_row*8 + atk_col]
                if (atk_sq._colour != king_colour and atk_sq._piece == 'k'):
                    return True

        # Knight checks
        knight_moves = [(1, 2), (1, -2), (-1, 2), (-1, -2), 
                         (2, 1), (2, -1), (-2, 1), (-2, -1)]
        for mv_row, mv_col in knight_moves:
            atk_row, atk_col = k_row + mv_row, k_col + mv_col
            if 0 <= atk_row <= 7 and 0 <= atk_col <= 7:
                atk_sq = self._chessboard[atk_row*8 + atk_col]
                if (atk_sq._colour != king_colour and atk_sq._piece == 'n'):
                    return True
        
        # Bishop, rook and queen (ray piece) checks
        brq_moves = [(-1, -1, 'bq'), (-1, 1, 'bq'), (1, -1, 'bq'), (1, 1, 'bq'),
                     (-1, 0, 'rq'), (0, -1, 'rq'), (1, 0, 'rq'), (0, 1, 'rq')]
        for mv_row, mv_col, p_str in brq_moves:
            atk_row, atk_col = k_row + mv_row, k_col + mv_col
            while 0 <= atk_row <= 7 and 0 <= atk_col <= 7:
                atk_num = atk_row*8 + atk_col
                atk_sq = self._chessboard[atk_num]
                if (atk_sq._colour != king_colour and atk_sq._piece in p_str):
                    return True
                elif atk_sq._colour != 'e':
                    break
                atk_row += mv_row
                atk_col += mv_col

        return False
      
    def _update_king(self, colour: str, sq_num: int) -> None:
        """Update variables containing information about king positions."""
        
        if colour == 'b':
            self._b_king_sq = sq_num
        else:
            self._w_king_sq = sq_num

    def get_legal_moves(self, from_num: int) -> List[int]:
        """
        Returns a list of squares available for legal moves.
        Castling TBA.
        """

        pseudolegal_moves = self.get_pseudolegal_moves(from_num)
        legal_moves = []
        from_sq = self._chessboard[from_num]
        from_colour = from_sq._colour
        from_piece = from_sq._piece

        if from_colour != self._to_move:
            return []

        for to_num in pseudolegal_moves:
            to_sq = self._chessboard[to_num]
            to_piece = to_sq._piece
            self.move_piece(from_num, to_num)
            if not self.is_in_check(from_colour):
                legal_moves.append(to_num)
            if to_piece != 'e':               
                from_sq.set_sq(from_colour, from_piece)
                to_sq.set_sq('b' if from_colour == 'w' else 'w', to_piece)
            else:
                # Handling en passant
                if from_piece == 'p' and to_num == self._ep_square:
                    if to_num > from_num:
                        self._chessboard[to_num - 8].set_sq('b' if 
                        from_colour == 'w' else 'w', to_piece)
                    else:
                        self._chessboard[to_num + 8].set_sq('b' if 
                        from_colour == 'w' else 'w', to_piece)
                self.move_piece(to_num, from_num)
        
        return legal_moves

    def make_move(self, from_num: int, to_num: int, 
                  promote_to: str = 'q') -> None:
        """
        Make a permanent move. Increments the halfmove clock as well as
        the fullmove counter, changes the en passant target square.
        Removal of castling rights TBA.
        """
        legal_moves = self.get_legal_moves(from_num)
        if to_num not in legal_moves:
            print("DEBUG: Illegal move")
            return None
        
        # Detecting possibility of en passant in next ply
        if self._chessboard[from_num]._piece == 'p':
            if to_num - from_num == 16:
                self._ep_square = to_num - 8
            elif to_num - from_num == -16:
                self._ep_square = to_num + 8
            else:
                self._ep_square = -1
        else:
            self._ep_square = -1

        mp_returnval = self.move_piece(from_num, to_num, promote_to)

        if mp_returnval > 0:
            self._halfmove_clock = 0
        else:
            self._halfmove_clock += 1

        if self._to_move == 'b':
            self._fullmove_counter += 1

        self._to_move = 'b' if self._to_move == 'w' else 'w'

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
        elif cmd in ('mm', 'm'):
            args = [int(arg) if arg not in 'bnrq' else arg for arg in args]
            board.make_move(*args)
        elif cmd in ('slm', 's'):
            board.show_legal_moves(board.alg_to_num(*args))
        elif cmd in ('slmn', 'sn'):
            board.show_legal_moves(int(*args))
        elif cmd in ('ff', 'fen', 'f'):
            fen_str = ''
            for arg in args:
                fen_str += arg + ' '
            board.import_fen(fen_str) if fen_str != '' else board.import_fen()
        elif cmd in ('i', 'iic'):
            print(board.is_in_check(*args))
        elif cmd in ('ant', 'num'):
            print(board.alg_to_num(*args))
        else:
            print('DEBUG: Unknown command')
