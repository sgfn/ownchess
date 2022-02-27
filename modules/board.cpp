#include <deque>
#include <iostream>
#include <unordered_set>
#include <string>
#include <vector>

// Colour definitions
#define CLR_ESC "\x1b[0m" // escape sequence
#define CLR_L_B "\x1b[0;30;46m" // light squares
#define CLR_L_W "\x1b[0;37;46m"
#define CLR_D_B "\x1b[0;30;44m" // dark squares
#define CLR_D_W "\x1b[0;37;44m"
#define CLR_H_B "\x1b[0;30;45m" // highlit squares
#define CLR_H_W "\x1b[0;37;45m"
// FEN string of initial position
#define FEN_INIT "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

struct square {
    char colour = 'e'; char piece = 'e'; char print();
};

char square::print() {
    switch(this->colour) {
        case 'w': return piece-32;
        case 'b': return piece;
        default: return ' ';
    }
}

struct move_record {
    int from_num, to_num;
    char from_piece, to_piece, move_type;
    bool can_castle[4];
    int ep_square, hm_clock, fm_counter;
    std::vector<std::pair<int, int>> legal_moves;
};

int alg_to_num(const std::string alg_coords) {
    return (alg_coords[1]-49)*8 + alg_coords[0]-97;
}

std::string num_to_alg(const int sq_num) {
    if (sq_num == -1) return "-";
    std::string alg_str = "";
    alg_str += (char)(sq_num % 8 + 97) + (char)(sq_num / 8 + 49);
    return alg_str;
}

class Board {
        static const std::unordered_set<int> EMPTY_SET;
        square chessboard[64];
        bool w_to_move; // true if white to move
        bool can_castle[4];
        int ep_square, hm_clock, fm_counter, w_king_square, b_king_square;
        std::vector<int> white_pieces, black_pieces, legal_moves;
        std::deque<move_record> move_history;
    public:
        Board();
        void print(const std::unordered_set<int> &);
        void set_fen(const std::string);
        void upd_king(const bool, const int);
        void upd_piece_v(const bool, const int, const int);
        void testing();
} the_board;

Board::Board() {
    this->white_pieces.reserve(16); this->black_pieces.reserve(16);
    this->legal_moves.reserve(218);
}

void Board::print(const std::unordered_set<int> &highlit_squares = EMPTY_SET) {
    std::string b_str = "";
    bool sq_light = true; // 56 (top left) is a light square
    for (int row=7; row>=0; row--) {
        for (int col=0; col<8; col++) {
            square * p = &this->chessboard[row*8+col];
            std::string clr_code;
            if (highlit_squares.count(row*8+col) > 0) {
                clr_code = ((*p).colour == 'w') ? CLR_H_W : CLR_H_B;
            }
            else if (sq_light) {
                clr_code = ((*p).colour == 'w') ? CLR_L_W : CLR_L_B;
            }
            else {
                clr_code = ((*p).colour == 'w') ? CLR_D_W : CLR_D_B;
            }
            b_str += clr_code + (*p).print() + ' ' + CLR_ESC;
            sq_light = !sq_light;
        }
        b_str += std::to_string(row + 1) + '\n';
        sq_light = !sq_light;
    }
    b_str += " A B C D E F G H";
    std::cout << b_str << std::endl;
}

void Board::set_fen(const std::string fen = FEN_INIT) {
    for (int i=0; i<64; i++) { // clear the board
        this->chessboard[i].colour = 'e'; this->chessboard[i].piece = 'e';
    }
    this->white_pieces.clear(); // clear the piece vectors
    this->black_pieces.clear();
    // Parse the FEN string
    int fen_field = 0; // helper variable for parsing the string
    int row = 0;
    int col = 0;

    for (int i=0; i<fen.length(); i++) {
        if (fen[i] == ' ') { // char is a space - increase helper variable
            fen_field++;
        }
        else {
            switch (fen_field) {
            case 0: // insert the pieces onto the chessboard
                if (fen[i] == '/') { // char is a slash - go to next row
                    col = 0;
                    row++;
                }
                else if (fen[i] >= 49 && fen[i] <= 56) { // char is a number - skip cols
                    col += fen[i]-48;
                }
                else { // char is a piece
                    char colour, piece;
                    if (fen[i] >= 65 && fen[i] <= 90) { // char is uppercase
                        colour = 'w';
                        piece = fen[i]+32;
                    }
                    else { // char is lowercase
                        colour = 'b';
                        piece = fen[i];
                    }
                    int sq_num = (7-row)*8 + col++; // unsure if that's correct, but would seem so
                    if (piece == 'k') { // update king squares
                        // TBA
                    }
                    this->chessboard[sq_num].colour = colour;
                    this->chessboard[sq_num].piece = piece;
                    // Update piece lists - TBA
                }
                break;
            case 1: // set the player to move, clear the castling rights
                this->w_to_move = (fen[i] == 'w');
                for (int i=0; i<4; i++) this->can_castle[i] = false;
                break;
            case 2: // set the correct castling rights
                switch (fen[i]) {
                    case 'K': this->can_castle[0] = true; break;
                    case 'Q': this->can_castle[1] = true; break;
                    case 'k': this->can_castle[2] = true; break;
                    case 'q': this->can_castle[3] = true; break;
                    default: break;
                }
                break;
            case 3: // set the ep square, default clock and counter values
                if (fen[i]!='-') {
                    char t[2] = {fen[i], fen[i+1]};
                    this->ep_square = alg_to_num(t);
                }
                else this->ep_square = -1;
                this->hm_clock = 0;
                this->fm_counter = 1;
                fen_field++; // hack to get rid of unwanted behaviour
                break;
            case 4: // NOP
                break;
            case 5: // set the clock and counter values
                // Convert a possibly longer number to int - TBA
                break;
            default:
                break;
            }
        }
    }
    // Update list of legal moves - TBA
    // Detect and handle game ending states - TBA
}

void Board::upd_king(const bool white, const int sq_to) {
    if (white) this->w_king_square = sq_to;
    else this->b_king_square = sq_to;
}

void Board::upd_piece_v(const bool white, const int sq_from, const int sq_to) {
    std::vector<int> *p_v = (white) ? &this->white_pieces : &this->black_pieces;
    if (sq_from == -1) {
        (*p_v).push_back(sq_to); return;
    }
    for (std::vector<int>::iterator p = (*p_v).begin(); p!=(*p_v).end(); p++) {
        if (*p == sq_from) {
            if (sq_to == -1) 
                (*p_v).erase(p);
            else 
                (*p_v).insert(p, sq_to);
            return;
        }
    }
    std::cerr << "DEBUG: Piece not found in vector\n";
}

void Board::testing() {
    
    
}

int main() {
    std::ios_base::sync_with_stdio(0);
    std::cin.tie(0);
    // the_board.update_piece_v('w', 16, 17);
    the_board.set_fen();
    the_board.print();
    the_board.testing();
    std::unordered_set<int> temp = {1, 2, 3, 4, 5, 6, 28};
    the_board.print(temp);
    for (std::unordered_set<int>::iterator p = temp.begin(); p != temp.end(); p++) {
        std::cout << *p << ' ';
    }
    return 0;
}