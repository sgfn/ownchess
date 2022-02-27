from typing import Dict, List, Tuple, Set
from time import time
import cython

class Square:
    """Class representing a single square in the board."""

    def __init__(self) -> None:
        """Create an empty Square object with the necessary properties."""

        self._colour = 'e'
        self._piece = 'e'
        # self._list_ind = -1
    
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

    # FEN string of initial position
    FEN_INIT = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    # Strings for interactive command prompt mode
    LOGO_STR = """
       #   #
      ##########                                    #
    ## ############                                 #
   ######### ########       ##   #   #  ###    ###  ###    ##     ##   ##
  # #####   ##########     #  #  #   #  #  #  #     #  #  #  #   #    #
  ####      ###########    #  #  # # #  #  #  #     #  #  ##      #    #
            ############    ##    # #   #  #   ###  #  #   ###  ###  ###
           #############
          ##############       b  o  a  r  d        m  o  d  u  l  e\n"""
    HELP_STR = """Available commands:\n\tq - exit\n\th - show this message
\tb - show board\n\tf [FEN] - set FEN, initial position if no FEN given
\tf get - get FEN of current position
\tl [square] - show legal moves from set square, print all if no square given
\tc - is current player in check\n\tm <square_from> <square_to> - make a move
\tu - undo the last move
\tp <depth> - run Perft from current position up to a specified depth
\te <code> - execute Python code (debug purposes only)"""

    # Board coordinates:
    #                   C O L U M N S
    #           0   1   2   3   4   5   6   7
    #
    #    8                                 63       7
    #    7                                          6
    #  r 6                                          5  R
    #  a 5                                          4  O
    #  n 4                                          3  W
    #  k 3                                          2  S - multiply by 8
    #  s 2      8   9  10  11   ...                 1
    #    1      0   1   2   3   4   5   6   7       0
    #
    #           A   B   C   D   E   F   G   H
    #                    f i l e s

    def __init__(self, fen: str = '') -> None:
        """
        Create a Board object with an 8x8 chessboard and set it up according 
        to given FEN (initial position if FEN not specified).
        """
        self._chessboard = [Square() for _ in range(64)]
        # Create variables to hold board properties
        self._to_move = '-'
        self._can_castle = [None, None, None, None] # K Q k q
        self._ep_square = -1
        self._halfmove_clock = -1
        self._fullmove_counter = -1

        # Create piece squares lists
        self._white_pieces = set()
        self._black_pieces = set()

        # # Create stable piece squares lists
        # self._white_piece_squares_nums_stable = [-1 for _ in range(16)]
        # self._black_piece_squares_nums_stable = [-1 for _ in range(16)]

        # # Disgusting hack to keep track of indices lost to ep (OH YEAH, COLOURS)
        # self._white_piece_indices_lost_to_ep = []
        # self._black_piece_indices_lost_to_ep = []

        # Create a move list to keep track of moves made
        self._move_history = []

        # Create a legal moves list
        self._all_legal_moves = []
        
        # Create helper properties containing the king's positions
        self._w_king_sq = -1
        self._b_king_sq = -1
        # Set the position from given FEN
        self.set_fen(fen)

    def __str__(self, highlit_squares: Set[int] = set()) -> str:
        """
        Return a string for printing the board (White's perspective) to stdout.
        Will highlight certain squares if passed a set of them as an argument.
        """
        s = ""
        sq_light = True  # 56 (top left) is a light square
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
        """Link to __str__() as some printing functions call __repr__()."""

        return self.__str__(*args)

    def alg_to_num(self, coords_str: str) -> int:
        """
        Convert algebraic notation of a square to a corresponding number 
        used by the board.
        """
        if len(coords_str) != 2:
            return -1
        rank, file_ord = int(coords_str[1]), ord(coords_str[0].lower())
        # file 'a' -> col 0, ord('a') = 97
        return (rank - 1) * 8 + (file_ord - 97)

    def num_to_alg(self, sq_num: int) -> str:
        """Convert square number used by the board to algebraic notation."""

        if sq_num == -1:
            return '-'
        rank = sq_num // 8 + 1
        file = chr(sq_num % 8 + 97)
        return f'{file}{rank}'

    def set_fen(self, fen: str = '') -> None:
        """
        Set the board up according to FEN (initial position if FEN 
        not specified). Does not check whether the FEN string is correct.
        """
        # Set initial position FEN if not specified
        if fen == '':
            fen = Board.FEN_INIT

        # Clear the board
        for square in self._chessboard:
            square._colour = 'e'
            square._piece = 'e'
            # square._list_ind = -1

        # Clear the piece lists UPDATE PIECE LISTS
        self._white_pieces = set()
        self._black_pieces = set()

        # Set the starting properties
        fen_data = fen.strip().split(' ')
        if len(fen_data) < 6:
            rows, self._to_move, cn_cs, ep_sq = fen_data
            hm_cl, fm_ct = 0, 1
        else:
            rows, self._to_move, cn_cs, ep_sq, hm_cl, fm_ct = fen_data
        
        # Convert the values
        for index, letter in enumerate(('K', 'Q', 'k', 'q')):
            self._can_castle[index] = True if letter in cn_cs else False
        self._ep_square = self.alg_to_num(ep_sq)
        self._halfmove_clock = int(hm_cl)
        self._fullmove_counter = int(fm_ct)

        # piece_list_black_i = 0
        # piece_list_white_i = 0
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
                    # Update king squares
                    if piece == 'k':
                        self._update_king(colour, sq_num)
                    self._chessboard[sq_num]._colour = colour
                    self._chessboard[sq_num]._piece = piece
                    # self._chessboard[sq_num]._list_ind = -1
                    # UPDATE PIECE LIST
                    self._update_piece_sets(colour, -1, sq_num)
                    # # UPDATE STABLE PIECE LIST AND SQUARE PROPERTY
                    # if colour == 'b':
                    #     self._chessboard[sq_num]._list_ind = piece_list_black_i
                    #     self._update_stable_piece_lists(colour, piece_list_black_i, sq_num)
                    #     piece_list_black_i += 1
                    # else:
                    #     self._chessboard[sq_num]._list_ind = piece_list_white_i
                    #     self._update_stable_piece_lists(colour, piece_list_white_i, sq_num)
                    #     piece_list_white_i += 1

                    col += 1
        
        # Update list of legal moves
        self._all_legal_moves = self.get_all_legal_moves()

        # Detect and handle game ending states
        self.detect_game_end()

    def get_fen(self) -> str:
        """
        Return a FEN string of the current position.
        Issue: returns EP square even if EP not possible (should be '-').
        """
        pcs = ''
        for sq_row in range(7, -1, -1):
            num = 0
            for sq_col in range(8):
                sq = self._chessboard[sq_row*8 + sq_col]
                if sq._colour == 'e':
                    num += 1
                else:
                    if num != 0:
                        pcs += str(num)
                    pcs += str(sq)
                    num = 0
            if num != 0:
                pcs += str(num)
            if sq_row != 0:
                pcs += '/'
        
        cn_cs = ''
        for index, letter in enumerate(('K', 'Q', 'k', 'q')):
            if self._can_castle[index]:
                cn_cs += letter
        cn_cs = '-' if cn_cs == '' else cn_cs

        to_mv, ep_sq, hm_cl, fm_ct = (self._to_move, self._ep_square, 
        self._halfmove_clock, self._fullmove_counter)
        
        return f'{pcs} {to_mv} {cn_cs} {self.num_to_alg(ep_sq)} {hm_cl} {fm_ct}'

    def get_pseudolegal_moves(self, sq_num: int) -> List[int]:
        """
        Return a list of squares available as targets of pseudolegal moves 
        (moves which might leave the player in check) from selected square.
        """
        from_sq = self._chessboard[sq_num]
        from_row, from_col = sq_num // 8, sq_num % 8
        pseudolegal_moves = []
        all_moves = []

        if from_sq._colour != self._to_move:
            return pseudolegal_moves
        
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

                # Castling
                tmp_iic_val = None
                cs_kingside_ind = 0 if from_sq._colour == 'w' else 2
                b = self._chessboard
                # Castling kingside
                if self._can_castle[cs_kingside_ind]:
                    if b[sq_num+1]._colour == b[sq_num+2]._colour == 'e':
                        # Test whether king is in check
                        tmp_iic_val = self.is_in_check()
                        if not tmp_iic_val:
                            pseudolegal_moves.append(sq_num + 2)
                # Castling queenside
                if self._can_castle[cs_kingside_ind + 1]:
                    if (b[sq_num-1]._colour == b[sq_num-2]._colour == 
                        b[sq_num-3]._colour == 'e'):
                        if tmp_iic_val is None:
                            tmp_iic_val = self.is_in_check()
                        if not tmp_iic_val:
                            pseudolegal_moves.append(sq_num - 2)
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

    def get_all_pseudolegal_moves(self) -> List[Tuple[int, int]]:

        all_pseudolegal_moves = []
        for sq_num in self._white_pieces if self._to_move == 'w' else self._black_pieces:
            for sq_to in self.get_pseudolegal_moves(sq_num):
                all_pseudolegal_moves.append((sq_num, sq_to))
        return all_pseudolegal_moves

    def is_in_check(self, other_player: bool = False) -> bool:
        """Test whether the player to move is in check."""

        if not other_player:
            k_colour = self._to_move
        else:
            k_colour = 'w' if self._to_move == 'b' else 'b'

        if k_colour == 'w':
            k_row, k_col = self._w_king_sq // 8, self._w_king_sq % 8
        else:
            k_row, k_col = self._b_king_sq // 8, self._b_king_sq % 8

        # Pawn checks
        pawn_move = 1 if k_colour == 'w' else -1
        pawn_moves = [(pawn_move, -1), (pawn_move, 1)]
        for mv_row, mv_col in pawn_moves:
            atk_row, atk_col = k_row + mv_row, k_col + mv_col
            if 0 <= atk_row <= 7 and 0 <= atk_col <= 7:
                atk_sq = self._chessboard[atk_row*8 + atk_col]
                if (atk_sq._colour != k_colour and atk_sq._piece == 'p'):
                    return True

        # "King checks" - illegal moves where both kings are on adjacent squares
        king_moves = [(1, 1), (1, 0), (1, -1), (0, 1),
                       (0, -1), (-1, 1), (-1, 0), (-1, -1)]
        for mv_row, mv_col in king_moves:
            atk_row, atk_col = k_row + mv_row, k_col + mv_col
            if 0 <= atk_row <= 7 and 0 <= atk_col <= 7:
                atk_sq = self._chessboard[atk_row*8 + atk_col]
                if (atk_sq._colour != k_colour and atk_sq._piece == 'k'):
                    return True

        # Knight checks
        knight_moves = [(1, 2), (1, -2), (-1, 2), (-1, -2), 
                         (2, 1), (2, -1), (-2, 1), (-2, -1)]
        for mv_row, mv_col in knight_moves:
            atk_row, atk_col = k_row + mv_row, k_col + mv_col
            if 0 <= atk_row <= 7 and 0 <= atk_col <= 7:
                atk_sq = self._chessboard[atk_row*8 + atk_col]
                if (atk_sq._colour != k_colour and atk_sq._piece == 'n'):
                    return True
        
        # Bishop, rook and queen (ray piece) checks
        brq_moves = [(-1, -1, 'bq'), (-1, 1, 'bq'), (1, -1, 'bq'), (1, 1, 'bq'),
                     (-1, 0, 'rq'), (0, -1, 'rq'), (1, 0, 'rq'), (0, 1, 'rq')]
        for mv_row, mv_col, p_str in brq_moves:
            atk_row, atk_col = k_row + mv_row, k_col + mv_col
            while 0 <= atk_row <= 7 and 0 <= atk_col <= 7:
                atk_num = atk_row*8 + atk_col
                atk_sq = self._chessboard[atk_num]
                if (atk_sq._colour != k_colour and atk_sq._piece in p_str):
                    return True
                elif atk_sq._colour != 'e':
                    break
                atk_row += mv_row
                atk_col += mv_col

        return False
      
    def get_legal_moves(self, from_num: int) -> List[Tuple[int, int]]:
        """
        Return a list of tuples representing legal moves from selected square.
        """
        pseudolegal_moves = self.get_pseudolegal_moves(from_num)
        legal_moves = []

        from_sq = self._chessboard[from_num]
        from_clr = from_sq._colour
        from_piece = from_sq._piece
        # from_index = from_sq._list_ind

        if from_clr != self._to_move:
            return legal_moves

        for to_num in pseudolegal_moves:
            to_sq = self._chessboard[to_num]
            to_piece = to_sq._piece
            # to_index = to_sq._list_ind

            # Castling - checking the square that king passes through
            if from_piece == 'k' and abs(to_num - from_num) == 2:
                # Determine if castling kingside or queenside
                cs_dir = 1 if to_num > from_num else -1

                self._move_piece(from_num, from_num + cs_dir)
                # Illegal if king is in check on the square it passes through
                if self.is_in_check():
                    self._move_piece(from_num + cs_dir, from_num)
                    continue
                # Unmove the piece, then proceed as normal
                self._move_piece(from_num + cs_dir, from_num)

            # Move the piece, see whether the king is in check, then unmove it
            self._move_piece(from_num, to_num)
            if not self.is_in_check():
                legal_moves.append((from_num, to_num))
            self._unmove_piece(from_num, to_num, from_clr, from_piece, to_piece) #, from_index, to_index)
        
        return legal_moves

    def show_legal_moves(self, sq_num: int) -> None:
        """Print the board with legal moves from selected square highlighted."""

        sq_set = set((to for fr, to in self._all_legal_moves if fr == sq_num))
        print(self.__str__(highlit_squares=sq_set))

    def show_piece_positions(self, colour: str) -> None: # UPDATE PIECE LISTS
        """Show piece positions on the output"""

        piece_positions = self._black_pieces if colour == 'b' else self._white_pieces
        print(self.__str__(highlit_squares=piece_positions))
    
    def get_all_legal_moves(self) -> List[Tuple[int, int]]:
        """Return a list of tuples representing all legal moves in position."""

        all_legal_moves = []
        for sq_num in self._white_pieces if self._to_move == 'w' else self._black_pieces:
            all_legal_moves.extend(self.get_legal_moves(sq_num))
        # # USING STABLE LISTS
        # for sq_num in self._white_piece_squares_nums_stable if self._to_move == 'w' else self._black_piece_squares_nums_stable:
        #     if sq_num != -1:
        #         square = self._chessboard[sq_num]
        #         if square._colour == self._to_move:
        #             all_legal_moves.extend(self.get_legal_moves(sq_num))

        return all_legal_moves

    def make_move(self, from_num: int, to_num: int, 
                  promote_to: str = 'q', perft_mode: bool = False) -> None:
        """
        Make a permanent move. Increments the halfmove clock as well as
        the fullmove counter, changes the en passant target square, 
        removes castling rights.
        """
        if not perft_mode:
            if (from_num, to_num) not in self._all_legal_moves:
                print(f'DEBUG: Illegal move: {str(self._chessboard[from_num])} on {self.num_to_alg(from_num)} -> {str(self._chessboard[to_num])} on {self.num_to_alg(to_num)}')
                print(f'\tPrevious move: {self._move_history[-1] if len(self._move_history) > 0 else "NONE"}')
                return None
        
        # Store board properties before making the move
        cn_cs = self._can_castle.copy()
        ep_sq = self._ep_square
        hm_cl = self._halfmove_clock
        fm_ct = self._fullmove_counter

        from_sq = self._chessboard[from_num]
        to_sq = self._chessboard[to_num]
        from_colour = from_sq._colour
        from_piece = from_sq._piece
        to_piece = to_sq._piece

        # from_index = from_sq._list_ind
        # to_index = to_sq._list_ind

        # Detecting loss of castling rights
        cs_kingside_ind = 0 if from_colour == 'w' else 2
        # # CHANGE: only check these conditions if there are castling rights to remove in the first place
        # if max(self._can_castle) == True: # stoopid change
        # King has moved from the starting square
        if from_num in (4, 60) and from_piece == 'k':
            self._can_castle[cs_kingside_ind] = False
            self._can_castle[cs_kingside_ind + 1] = False
        # Rook has moved from the starting square
        elif from_num in (0, 7, 56, 63) and from_piece == 'r':
            if (from_num, from_colour) in ((7, 'w'), (63, 'b')):
                self._can_castle[cs_kingside_ind] = False
            elif (from_num, from_colour) in ((0, 'w'), (56, 'b')):
                self._can_castle[cs_kingside_ind + 1] = False
        # Rook was captured
        elif to_num in (0, 7, 56, 63) and to_piece == 'r':
            # Capturing the rook removes castling rights for the opponent
            cs_kingside_ind = 0 if cs_kingside_ind == 2 else 2
            if (to_num, from_colour) in ((7, 'b'), (63, 'w')):
                self._can_castle[cs_kingside_ind] = False
            elif (to_num, from_colour) in ((0, 'b'), (56, 'w')):
                self._can_castle[cs_kingside_ind + 1] = False

        # Move the piece and check whether to reset the halfmove clock
        reset_hm_cl, move_type = self._move_piece(from_num, to_num, promote_to, True)
        if reset_hm_cl > 0:
            self._halfmove_clock = 0
        else:
            self._halfmove_clock += 1

        if self._to_move == 'b':
            self._fullmove_counter += 1

        self._to_move = 'b' if self._to_move == 'w' else 'w'

        # Update the list of previous moves
        move_data = [from_num, to_num, from_piece, to_piece, # from_index, to_index, 
        move_type, cn_cs, ep_sq, hm_cl, fm_ct, self._all_legal_moves.copy()]
        self._move_history.append(move_data)

        # Detecting possibility of en passant in next ply
        if from_piece == 'p':
            if to_num - from_num == 16:
                self._ep_square = to_num - 8
            elif to_num - from_num == -16:
                self._ep_square = to_num + 8
            else:
                self._ep_square = -1
        else:
            self._ep_square = -1

        # Update the list of legal moves
        self._all_legal_moves = self.get_all_legal_moves()

        # Detect and handle game ending states
        if not perft_mode:
            self.detect_game_end()

    def unmake_move(self) -> None:
        """Unmake the last move made using the make_move() function."""

        if len(self._move_history) == 0:
            print('DEBUG: Nothing to unmake')
            return None

        # Unpack and update the list of previous moves
        (from_num, to_num, from_piece, to_piece, # from_index, to_index, 
        move_type, cn_cs, ep_sq, hm_cl, fm_ct, moves_cache) = self._move_history.pop()
        
        # Reinstate previous board properties
        self._can_castle = cn_cs.copy()
        self._ep_square = ep_sq
        self._halfmove_clock = hm_cl
        self._fullmove_counter = fm_ct

        has_moved = 'w' if self._to_move == 'b' else 'b'
        # Unmake the move
        self._unmove_piece(from_num, to_num, has_moved, from_piece, to_piece, # from_index, to_index, 
                           True)

        # Change the player to move
        self._to_move = has_moved

        # Load the list of legal moves from cache
        self._all_legal_moves = moves_cache

    def detect_game_end(self, verbose: bool = False) -> int:
        """
        Detect and handle game ending states - stalemates and checkmates.
        Returns 1 if checkmate, 2 if stalemate, 0 otherwise.
        """
        if len(self._all_legal_moves) == 0:
            if self.is_in_check():
                if verbose:
                    colour = 'White' if self._to_move == 'b' else 'Black'
                    print(f'Checkmate. {colour} wins')
                return 1
            else:
                if verbose:
                    print('Stalemate')
                return 2
        return 0

    def perft(self, depth: int) -> int:
        """
        Return number of leaf nodes (possible positions after all legal moves)
        at set depth from current position.
        """
        if depth < 0:
            raise ValueError('Negative depth')
        if depth == 0:
            return 1
        if depth == 1:
            counter = 0
            for move_from, move_to in self._all_legal_moves:
                if self._chessboard[move_from]._piece == 'p' and move_to // 8 in (0, 7):
                   counter += 3
                counter += 1
            return counter

        leaf_nodes = 0
        for move_from, move_to in self._all_legal_moves:
            # Handling promotions
            if self._chessboard[move_from]._piece == 'p' and move_to // 8 in (0, 7):
                for promote_to in ('q', 'r', 'b', 'n'):
                    self.make_move(move_from, move_to, promote_to, True)
                    leaf_nodes += self.perft(depth - 1)
                    self.unmake_move()
            else:
                self.make_move(move_from, move_to, 'q', True)
                leaf_nodes += self.perft(depth - 1)
                self.unmake_move()
        return leaf_nodes

    def perft_devel(self, depth: int) -> int:
        """
        Return number of leaf nodes (possible positions after all legal moves)
        at set depth from current position.
        """
        raise NotImplementedError()
        if depth < 0:
            raise ValueError('Negative depth')
        if depth == 0:
            return 1
        if depth == 1:
            counter = 0
            for move_from, move_to in self._all_legal_moves:
                if self._chessboard[move_from]._piece == 'p' and move_to // 8 in (0, 7):
                   counter += 3
                counter += 1
            return counter

        leaf_nodes = 0
        pseudolegal_moves = self.get_all_pseudolegal_moves()
        for move_from, move_to in pseudolegal_moves:
            # Handling promotions
            if self._chessboard[move_from]._piece == 'p' and move_to // 8 in (0, 7):
                self.make_move(move_from, move_to, 'q', True)
                if not self.is_in_check(other_player=True):
                    leaf_nodes += self.perft_devel(depth - 1)
                    self.unmake_move()
                else:
                    self.unmake_move()
                    continue

                for promote_to in ('r', 'b', 'n'):
                    self.make_move(move_from, move_to, promote_to, True)
                    leaf_nodes += self.perft_devel(depth - 1)
                    self.unmake_move()
            else:
                self.make_move(move_from, move_to, 'q', True)
                if not self.is_in_check(other_player=True):
                    leaf_nodes += self.perft_devel(depth - 1)
                self.unmake_move()
        return leaf_nodes

    def divide(self, depth: int) -> Dict[str, int]:
        """Perft variation listing the node counts for each possible move."""

        if depth < 2:
            return self.perft(depth)

        leaf_nodes_dict = {}
        for move_from, move_to in self._all_legal_moves:
            # Handling promotions
            if self._chessboard[move_from]._piece == 'p' and move_to // 8 in (0, 7):
                for promote_to in ('q', 'r', 'b', 'n'):
                    self.make_move(move_from, move_to, promote_to, True)
                    leaf_nodes_dict[f'{self.num_to_alg(move_from)}{self.num_to_alg(move_to)}{promote_to.upper()}'] = self.perft(depth - 1)
                    self.unmake_move()
            else:
                self.make_move(move_from, move_to, 'q', True)
                leaf_nodes_dict[f'{self.num_to_alg(move_from)}{self.num_to_alg(move_to)}'] = self.perft(depth - 1)
                self.unmake_move()

        return leaf_nodes_dict

    def interactive_mode(self) -> None:
        """Work with the board in an interactive command prompt mode."""

        print("Interactive command prompt mode\nType 'h' for help, 'q' to quit")
        active = True
        while active:
            cmd, *args = input().strip().split()
            if cmd in ('q', 'qqq', 'quit', 'exit'):
                active = False
            elif cmd in ('h', 'help'):
                print(Board.HELP_STR)
            elif cmd in ('b', 'board'):
                print(self)
            elif cmd in ('c', 'iic', 'check'):
                print(self.is_in_check())
           
            elif cmd in ('f', 'fen'):
                if len(args) == 1 and args[0] == 'get':
                    print(self.get_fen())
                else:
                    fen = ''
                    for arg in args:
                        fen += arg + ' '
                    self.set_fen(fen)

            elif cmd in ('l', 'slm', 'legal'):
                if len(args) == 1:
                    self.show_legal_moves(self.alg_to_num(*args))
                else:
                    i = 0
                    t_list = self._all_legal_moves
                    for from_move, to_move in t_list:
                        print(self.num_to_alg(from_move), self.num_to_alg(to_move), sep='', end=', ' if i != len(t_list)-1 else '\n')
                        i += 1
            
            elif cmd in ('s', 'spp', 'pieces'):
                self.show_piece_positions(*args)

            elif cmd in ('m', 'mm', 'move'):
                from_num = self.alg_to_num(args[0])
                to_num = self.alg_to_num(args[1])
                promote_to = 'q'
                if len(args) > 2:
                    promote_to = args[2]
                self.make_move(from_num, to_num, promote_to)
            
            elif cmd in ('u', 'um', 'undo', 'umove', 'unmove'):
                self.unmake_move()
 
            elif cmd in ('e', 'exec'):
                to_exec = ''
                for arg in args:
                    to_exec += arg + ' '
                exec(to_exec.rstrip())

            elif cmd in ('p', 'perft'):
                start_time = time()
                nodes = self.perft(int(*args))
                total_time = round(time() - start_time, 2)
                print(f'Nodes: {nodes} \tTime: {total_time} s \tSpeed: {int(nodes//(total_time*1000)) if total_time != 0 else "Inf"} knodes/s')
            
            elif cmd in ('d', 'divide'):
                start_time = time()
                ans_dict = self.divide(int(*args))
                for move, count in ans_dict.items():
                    print(f'{move}: {count}')
                print(f'\nNodes total: {sum(ans_dict.values())}')
                print(f'Time: {round(time() - start_time, 2)} s')
            else:
                print(f'Unknown command: {cmd}')
    
    def _add_piece(self, colour: str, piece: str, sq_num: int, # index: int
                    ) -> None:
        """
        Internal method. For all normal purposes use make_move() 
        or set_fen() instead.
        Add a piece at the specified coordinates (numerical).
        """
        to_sq = self._chessboard[sq_num]
        # if to_sq._colour != 'e':
        #     print(f'DEBUG: Square {sq_num} is occupied, replacing')

        if piece == 'k':
            self._update_king(colour, sq_num)

        to_sq._colour = colour
        to_sq._piece = piece
        # to_sq._list_ind = index
    
    def _move_piece(self, from_num: int, to_num: int = -1, promote_to: str = 'q', 
                    update_lists: bool = False) -> Tuple[int, str]:
        """
        Internal method. For all normal purposes use make_move() instead.
        Move/remove a single piece (numerical coordinates). Returns a tuple of
        two values, the first one is positive if move resets the halfmove 
        counter: 1 - pawn move, 2 - capture, 0 - neither; the second one returns
        a one-character string depicting type of move: 'e' - en passant,
        'c' - castling, 'q'/'r'/'b'/'n' - promotion to the respective piece,
        's' - other move (can be a capture).
        """
        reset_hm_cl = 0
        move_type = 's'
        from_sq = self._chessboard[from_num]
        from_colour = from_sq._colour
        # from_index = from_sq._list_ind
        their_colour = 'b' if from_colour == 'w' else 'w'

        if from_colour == 'e':
            print(f'DEBUG: Square {from_num} is empty')
            return None

        if from_sq._piece == 'k':
            self._update_king(from_colour, to_num)
            # Handling castling moves
            if from_num in (4, 60) and abs(to_num - from_num) == 2:
                move_type = 'c'

                if to_num > from_num: # castling kingside
                    rook_from = from_num + 3
                    rook_to = from_num + 1
                else: # castling queenside
                    rook_from = from_num - 4
                    rook_to = from_num - 1

                self._chessboard[rook_to]._colour = from_colour
                self._chessboard[rook_to]._piece = 'r'
                self._chessboard[rook_from]._colour = 'e'
                self._chessboard[rook_from]._piece = 'e'

                # rook_ind = self._chessboard[rook_from]._list_ind
                # self._chessboard[rook_to]._list_ind = rook_ind
                # self._chessboard[rook_from]._list_ind = -1

                # UPDATE PIECE LISTS
                if update_lists:
                    self._update_piece_sets(from_colour, rook_from, rook_to)
                    # # UPDATE STABLE PIECE LISTS
                    # self._update_stable_piece_lists(from_colour, rook_ind, rook_to)

        # Standard capture
        if to_num != -1:
            if self._chessboard[to_num]._colour == their_colour: # this index will get changed later
                reset_hm_cl = 2
                # UPDATE PIECE LISTS
                if update_lists:
                    self._update_piece_sets(their_colour, to_num, -1)
                    # # UPDATE STABLE PIECE LISTS
                    # self._update_stable_piece_lists(their_colour, self._chessboard[to_num]._list_ind, -1)

        if from_sq._piece == 'p':
            # Handling promotions
            pr_row = 7 if from_colour == 'w' else 0
            if to_num // 8 == pr_row:
                move_type = promote_to
                self._add_piece(from_colour, promote_to, to_num)
                # UPDATE PIECE LISTS
                if update_lists:
                    self._update_piece_sets(from_colour, from_num, to_num)
                    # # UPDATE STABLE PIECE LISTS
                    # self._update_stable_piece_lists(from_colour, from_index, to_num)
                to_num = -1
            
            # Handling en passant
            elif to_num == self._ep_square:
                move_type = 'e'
                ep_pawn_sq = to_num - 8 if to_num > from_num else to_num + 8

                self._chessboard[ep_pawn_sq]._colour = 'e'
                self._chessboard[ep_pawn_sq]._piece = 'e'
                
                # ep_pawn_index = self._chessboard[ep_pawn_sq]._list_ind
                # self._chessboard[ep_pawn_sq]._list_ind = -1
                # UPDATE PIECE LISTS
                if update_lists:
                    self._update_piece_sets(their_colour, ep_pawn_sq, -1)
                    # # UPDATE STABLE PIECE LISTS
                    # self._update_stable_piece_lists(their_colour, ep_pawn_index, -1)

                # # UPDATE THE ABOMINATIONS
                # abomination = self._white_piece_indices_lost_to_ep if from_colour == 'b' else self._black_piece_indices_lost_to_ep
                # abomination.append(ep_pawn_index)

            reset_hm_cl = 1

        # Actually move the piece
        if to_num != -1:
            self._chessboard[to_num]._colour = from_colour
            self._chessboard[to_num]._piece = from_sq._piece
            # self._chessboard[to_num]._list_ind = from_index

        from_sq._colour = 'e'
        from_sq._piece = 'e'
        # from_sq._list_ind = -1

        # UPDATE PIECE LISTS
        if update_lists:
            if move_type not in ('q', 'r', 'b', 'n'):
                self._update_piece_sets(from_colour, from_num, to_num)
                # # UPDATE STABLE PIECE LISTS
                # self._update_stable_piece_lists(from_colour, from_index, to_num)

        return (reset_hm_cl, move_type)

    def _unmove_piece(self, from_num: int, to_num: int, from_colour: str, 
                      from_piece: str, to_piece: str, # from_index: int, to_index: int, 
                      update_sets: bool = False) -> None:
        """
        Internal method. For all normal purposes use unmake_move() instead.
        Undo a move made using the _move_piece(from_num, to_num) method.
        """
        from_sq = self._chessboard[from_num]
        to_sq = self._chessboard[to_num]

        their_colour = 'w' if from_colour == 'b' else 'b'

        # Move was a standard capture
        if to_piece != 'e':
            from_sq._colour = from_colour
            from_sq._piece = from_piece
            to_sq._colour = their_colour
            to_sq._piece = to_piece
            # from_sq._list_ind = from_index
            # to_sq._list_ind = to_index

            # UPDATE PIECE LISTS
            if update_sets:
                self._update_piece_sets(their_colour, -1, to_num)
                # # UPDATE STABLE PIECE LISTS
                # self._update_stable_piece_lists(their_colour, to_index, to_num)
        
        # Move was either en passant or not a capture (possibly castling)
        else:
            # Handling en passant
            if from_piece == 'p' and to_num == self._ep_square:
                ep_pawn_sq = to_num - 8 if to_num > from_num else to_num + 8
                self._chessboard[ep_pawn_sq]._colour = their_colour
                self._chessboard[ep_pawn_sq]._piece = 'p'

                # lost_index = self._white_piece_indices_lost_to_ep.pop() if from_colour == 'b' else self._black_piece_indices_lost_to_ep.pop()
                # # WHAT THE FUCK IS HAPPENING
                # self._chessboard[ep_pawn_sq]._list_ind = lost_index

                # UPDATE PIECE LISTS
                if update_sets:
                    self._update_piece_sets(their_colour, -1, ep_pawn_sq)
                    # # UPDATE STABLE PIECE LISTS
                    # self._update_stable_piece_lists(their_colour, lost_index, ep_pawn_sq)

            # Handling castling moves
            elif from_piece == 'k' and abs(to_num - from_num) == 2:
                if to_num > from_num: # castling kingside
                    rook_from = from_num + 3
                    rook_to = from_num + 1
                else: # castling queenside
                    rook_from = from_num - 4
                    rook_to = from_num - 1

                self._chessboard[rook_to]._colour = 'e'
                self._chessboard[rook_to]._piece = 'e'
                self._chessboard[rook_from]._colour = from_colour
                self._chessboard[rook_from]._piece = 'r'

                # rook_index = self._chessboard[rook_to]._list_ind
                # self._chessboard[rook_to]._list_ind = -1
                # self._chessboard[rook_from]._list_ind = rook_index

                # UPDATE PIECE LISTS
                if update_sets:
                    self._update_piece_sets(from_colour, rook_to, rook_from)
                    # # UPDATE STABLE PIECE LISTS
                    # self._update_stable_piece_lists(from_colour, rook_index, rook_from)
    
            self._move_piece(to_num, from_num, 'q', False)
        
        # UPDATE PIECE LISTS
        if update_sets:
            self._update_piece_sets(from_colour, to_num, from_num)
            # # UPDATE STABLE PIECE LISTS
            # self._update_stable_piece_lists(from_colour, from_index, from_num)
        
        # Cleaning up after unmaking a promotion
        if from_piece != from_sq._piece:
            from_sq._piece = from_piece

        # Update king position
        if from_piece == 'k':
            self._update_king(from_colour, from_num)

    def _update_king(self, colour: str, sq_num: int) -> None:
        """Update variables containing information about king positions."""
        
        if colour == 'b':
            self._b_king_sq = sq_num
        else:
            self._w_king_sq = sq_num

    def _update_piece_sets(self, colour: str, sq_from: int, sq_to: int) -> None:

        p_set = self._black_pieces if colour == 'b' else self._white_pieces 
        if sq_from != -1:
            p_set.remove(sq_from)
        if sq_to != -1:
            p_set.add(sq_to)

    def _update_stable_piece_lists(self, colour: str, index: int, sq_to: int) -> None:
        raise NotImplementedError()

        p_list = self._black_piece_squares_nums_stable if colour == 'b' else self._white_piece_squares_nums_stable
        p_list[index] = sq_to
        

print(Board.LOGO_STR)

if __name__ == '__main__':
    board = Board()
    board.interactive_mode()
