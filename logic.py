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
        self.board = [[None for _ in range(8)] for _ in range(8)]

    def __str__(self) -> str:
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

                b_data += ' '+COL_ESC
                field_light = not field_light
            b_data += str(row_num) + '\n'
            row_num -= 1
            field_light = not field_light
        b_data += ' A B C D E F G H'
        return b_data

    def __repr__(self) -> str:
        return self.__str__()

    def setup(self) -> None:
        data = ('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r')
        for i in range(8):
            self.board[0][i] = Piece('b', data[i])
            self.board[1][i] = Piece('b', 'p')
            self.board[6][i] = Piece('w', 'p')
            self.board[7][i] = Piece('w', data[i])
        for i in range(2, 6):
            self.board[i] = [None for _ in range(8)]

    def move_algebraic(self, alg_str: str) -> Tuple[int, int]:
        files = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        to_tuple = (8-int(alg_str[1]), files[alg_str[0].lower()])
        return to_tuple

    def move(self, from_tpl: Tuple[int, int], to_tpl: Tuple[int, int]) -> None:
        from_row, from_col = from_tpl
        to_row, to_col = to_tpl
        if self.board[from_row][from_col] == None:
            print('DEBUG: Nothing to move')
            return None
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None


class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.board.setup()
        self.to_move = 'w'


if __name__ == '__main__':
    gm = Game()
    print(gm.board)
