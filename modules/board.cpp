#include <deque>
#include <iostream>
#include <forward_list>
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
// Strings for interactive command prompt mode
#define LOGO_STR "\n       #   #\n      ##########                             \
       #\n    ## ############                                 #\n   ######### #\
#######       ##   #   #  ###    ###  ###    ##     ##   ##\n  # #####   ######\
####     #  #  #   #  #  #  #     #  #  #  #   #    #\n  ####      ########### \
   #  #  # # #  #  #  #     #  #  ##      #    #\n            ############    #\
#    # #   #  #   ###  #  #   ###  ###  ###\n           #############\n        \
  ##############       b  o  a  r  d        m  o  d  u  l  e\n"
#define WELCOME_STR "Interactive command prompt mode\nType 'h' for help, 'q' to\
 quit"
#define HELP_STR "Available commands:\n\tq - exit\n\th - show this message\n\
\tb - show board\n\tf [FEN] - set FEN, initial position if no FEN given\n\
\tf get - get FEN of current position\n\
\tl [square] - show legal moves from set square, print all if no square given\n\
\tc - is current player in check\n\tm <square_from> <square_to> - make a move\n\
\tu - undo the last move\n\
\tp <depth> - run Perft from current position up to a specified depth\n"

typedef std::forward_list<int> flInt;
typedef std::pair<int, int> pIntInt;
typedef std::unordered_set<int> usInt;
typedef std::vector<int> vInt;
typedef std::vector<pIntInt> vPIntInt;

struct square {
    char colour = 'e'; char piece = 'e'; char print();
};

char square::print() {
    if (this->colour == 'e') return ' ';
    else if (this->colour == 'w') return piece-32;
    else return piece;
}

struct move_record {
    int from_num, to_num;
    char from_piece, to_piece, move_type;
    bool can_castle[4];
    int ep_square, hm_clock, fm_counter;
    vPIntInt legal_moves;
};

int alg_to_num(const std::string alg_coords) {
    return ((alg_coords[1]-49)<<3) + alg_coords[0]-97;
}

std::string num_to_alg(const int sq_num) {
    if (sq_num == -1) return "-";
    std::string alg_str = "";
    alg_str += (char)((sq_num&7) + 97) + (char)((sq_num>>3) + 49);
    return alg_str;
}

class Board {
        square chessboard[64];
        bool w_to_move; // true if white to move
        bool can_castle[4];
        int ep_square, hm_clock, fm_counter, w_king_square, b_king_square;
        flInt w_pcs, b_pcs; // piece lists
        vInt legal_moves;
        std::deque<move_record> move_history;
        void _upd_king(const bool, const int);
        void _upd_piece_l(const bool, const int, const int);
    public:
        Board(const std::string);
        void print();
        void print(const flInt &);
        void print(const usInt &);
        void set_fen(const std::string);
        std::string get_fen();
        vInt get_pseudolegal_moves(const int);
        vPIntInt get_all_pseudolegal_moves();
        bool is_in_check();
        bool is_in_check(const bool);
        void interactive_mode();
        void testing();
};

Board::Board(const std::string fen = FEN_INIT) {
    this->legal_moves.reserve(218);
    this->set_fen(fen);
}

void Board::print() {
    const usInt empty_set; // disgusting hack, TODO: rewrite
    this->print(empty_set);
}

void Board::print(const flInt &h_sqrs_l) {
    usInt h_sqrs_s;
    h_sqrs_s.insert(h_sqrs_l.begin(), h_sqrs_l.end());
    this->print(h_sqrs_s);
}

void Board::print(const usInt &highlit_squares) {
    std::string b_str = "";
    bool sq_light = true; // 56 (top left) is a light square
    for (int row=7; row>=0; row--) {
        for (int col=0; col<8; col++) {
            square * p = &this->chessboard[(row<<3)+col];
            std::string clr_code;
            if (highlit_squares.count((row<<3)+col) > 0) {
                clr_code = (p->colour == 'w') ? CLR_H_W : CLR_H_B;
            }
            else if (sq_light) {
                clr_code = (p->colour == 'w') ? CLR_L_W : CLR_L_B;
            }
            else {
                clr_code = (p->colour == 'w') ? CLR_D_W : CLR_D_B;
            }
            b_str += clr_code + p->print() + ' ' + CLR_ESC;
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
    this->w_pcs.clear(); this->b_pcs.clear(); // clear the piece lists
    // Parse the FEN string
    int fen_field = 0, row = 0, col = 0; // fen_field - helper var for parsing
    char ch;
    for (int i=fen.find_first_not_of(' '); i<fen.length(); i++) {
        ch = fen[i];
        if (ch == ' ') { // ch is a space - increase helper variable
            fen_field++;
        }
        else {
            if (fen_field==0) { // insert the pieces onto the chessboard
                if (ch == '/') { // ch is a slash - go to next row
                    col = 0;
                    row++;
                }
                else if (ch >= 49 && ch <= 56) { // ch is a number - skip cols
                    col += ch-48;
                }
                else { // ch is a piece
                    char colour, piece;
                    bool white = (ch >= 65 && ch <= 90); // is ch uppercase
                    int sq_num = ((7-row)<<3) + col++;
                    if (piece == 'k') { // update king squares
                        this->_upd_king(white, sq_num);
                    }
                    this->chessboard[sq_num].colour = (white) ? 'w' : 'b';
                    this->chessboard[sq_num].piece = (white) ? ch+32 : ch;
                    // Update piece lists
                    this->_upd_piece_l(white, -1, sq_num);
                }
            }
            else if (fen_field==1) { // set the player to move, clear can_castle
                this->w_to_move = (ch == 'w');
                for (int i=0; i<4; i++) this->can_castle[i] = false;
            }
            else if (fen_field==2) { // set the correct castling rights
                switch (ch) {
                    case 'K': this->can_castle[0] = true; break;
                    case 'Q': this->can_castle[1] = true; break;
                    case 'k': this->can_castle[2] = true; break;
                    case 'q': this->can_castle[3] = true; break;
                    default: break;
                }
            }
            else if (fen_field==3) { // set ep square, def clock & counter vals
                if (ch!='-') {
                    char t[2] = {ch, fen[++i]};
                    this->ep_square = alg_to_num(t);
                }
                else this->ep_square = -1;
                this->hm_clock = 0;
                this->fm_counter = 1;
            }
            else if (fen_field==4) { // set the clock and counter values
                int sp_pos = fen.find_first_of(' ', i);
                this->hm_clock = std::stoi(fen.substr(i, sp_pos-i));
                this->fm_counter = std::stoi(fen.substr(sp_pos+1)); // TODO: fix additional space at the end of string
                break;
            }
            else break;
        }
    }
    // Update list of legal moves - TBA
    // Detect and handle game ending states - TBA
}

std::string Board::get_fen() {
    std::string pcs = "";
    int num;
    for (int row=7; row>=0; row--) {
        num = 0;
        for (int col=0; col<8; col++) {
            square* sq = &this->chessboard[(row<<3)+col];
            if (sq->colour == 'e') num++;
            else {
                if (num!=0) pcs += std::to_string(num);
                pcs += sq->print();
                num = 0;
            }
        }
        if (num!=0) pcs += std::to_string(num);
        if (row!=0) pcs += '/';
    }
    char to_mv = (this->w_to_move) ? 'w' : 'b';
    std::string cn_cs = "";
    char aid[4] = {'K', 'Q', 'k', 'q'};
    for (int i=0; i<4; i++) {
        if (this->can_castle[i]) cn_cs += aid[i];
    }
    if (cn_cs == "") cn_cs = "-";
    return pcs + ' ' + to_mv + ' ' + cn_cs + ' ' + num_to_alg(this->ep_square) 
           + ' ' + std::to_string(this->hm_clock) + ' '
           + std::to_string(this->fm_counter);
}

vInt Board::get_pseudolegal_moves(const int sq_num) {
    square* from_sq = &this->chessboard[sq_num];
    int from_row = sq_num>>3, from_col = sq_num&7;
    char from_colour = from_sq->colour;
    bool from_white = (from_colour == 'w');
    vPIntInt all_moves;
    vInt plegal_moves;
    char pc = from_sq->piece;
    if (from_white != this->w_to_move) return plegal_moves;
    else if (pc == 'p') {
        int start_row = (from_white) ? 1 : 6;
        int mv_num = (from_white) ? 8 : -8;
        int dest_num = sq_num;
        square* to_sq;
        for (int i=0; i<2; ++i) {
            if (from_row != start_row) ++i; // will get called twice for no reason, TODO: maybe fix
            dest_num += mv_num;
            // Cannot advance pawns onto occupied squares
            if (this->chessboard[dest_num].colour != 'e') break;
            plegal_moves.push_back(dest_num);
        }
        int mv_col[2] = {-1, 1};
        char opp_colour = (from_colour == 'w') ? 'b' : 'w';
        for (int i=0; i<2; ++i) {
            if (0 <= from_col+mv_col[i] && from_col+mv_col[i] <= 7) { // will do unnecessary checks twice, TODO: maybe fix
                dest_num = sq_num + mv_num + mv_col[i];
                to_sq = &this->chessboard[dest_num];
                // Standard pawn capture, en passant capture
                if (to_sq->colour==opp_colour || dest_num==this->ep_square) {
                    plegal_moves.push_back(dest_num);
                }
            }
        }
    }
    else if (pc == 'k' || pc == 'n') {
        if (pc == 'k') {
            all_moves = {{1, 1}, {1, 0}, {1, -1}, {0, 1}, 
                         {0, -1}, {-1, 1}, {-1, 0}, {-1, -1}};
            // Castling
            int cs_kside_index = (from_white) ? 0 : 2;
            square* b = this->chessboard;
            int tmp_iic_val = -1; // helper var for storing is_in_check() result
            if (this->can_castle[cs_kside_index]) { // castling kingside
                for (int i=1; i<3; ++i) {
                    if (b[sq_num+i].colour != 'e') break;
                    if (i == 2) { // TODO: consider rewriting this bit of code
                        tmp_iic_val = (this->is_in_check()) ? 1 : 0;
                        if (tmp_iic_val==0) plegal_moves.push_back(sq_num+2);
                    }
                }
            }
            if (this->can_castle[cs_kside_index+1]) { // castling queenside
                for (int i=1; i<4; ++i) {
                    if (b[sq_num-i].colour != 'e') break;
                    if (i==3) { // TODO: see above
                        if (tmp_iic_val == -1) 
                            tmp_iic_val = (this->is_in_check()) ? 1 : 0;
                        if (tmp_iic_val==0) plegal_moves.push_back(sq_num-2);
                    }
                }
            }
        }
        else {
            all_moves = {{1, 2}, {1, -2}, {-1, 2}, {-1, -2}, 
                         {2, 1}, {2, -1}, {-2, 1}, {-2, -1}};
        }
        int dest_row, dest_col, dest_num;
        for (pIntInt pair : all_moves) {
            dest_row = from_row + pair.first;
            dest_col = from_col + pair.second;
            if (0<=dest_row && dest_row<=7 && 0<=dest_col && dest_col<=7) {
                dest_num = (dest_row<<3) + dest_col;
                if (this->chessboard[dest_num].colour != from_colour) {
                    plegal_moves.push_back(dest_num);
                }
            }
        }
    }
    else { // ray pieces
        if (pc != 'r')
            all_moves.insert(all_moves.end(), {{-1,-1}, {-1,1}, {1,-1}, {1,1}});
        if (pc != 'b')
            all_moves.insert(all_moves.end(), {{-1,0}, {0,-1}, {1,0}, {0,1}});
        int dest_row, dest_col, dest_num;
        square* to_sq;
        for (pIntInt pair : all_moves) {
            dest_row = from_row + pair.first;
            dest_col = from_col + pair.second;
            while (0<=dest_row && dest_row<=7 && 0<=dest_col && dest_col<=7) {
                dest_num = (dest_row<<3) + dest_col;
                to_sq = &this->chessboard[dest_num];
                if (to_sq->colour == 'e') plegal_moves.push_back(dest_num);
                else {
                    if (to_sq->colour != from_colour)
                        plegal_moves.push_back(dest_num);
                    break;
                }
                dest_row += pair.first;
                dest_col += pair.second;
            }
        }
    }
    return plegal_moves;
}

vPIntInt Board::get_all_pseudolegal_moves() {
    vPIntInt all_plegal_moves;
    flInt* p = (this->w_to_move) ? &this->w_pcs : &this->b_pcs;
    for (int sq_num : *p) {
        for (int sq_to : this->get_pseudolegal_moves(sq_num))
            all_plegal_moves.push_back(std::make_pair(sq_num, sq_to));
    }
    return all_plegal_moves;
}

bool Board::is_in_check() {
    return this->is_in_check(true);
}

bool Board::is_in_check(const bool curr_player) {
    const bool w_king = (curr_player) ? this->w_to_move : !this->w_to_move;
    int k_row = (w_king) ? w_king_square>>3 : b_king_square>>3;
    int k_col = (w_king) ? w_king_square&7 : b_king_square&7; // TODO: consider rewriting
    // TBA
    return false;
}

void Board::interactive_mode() {
    std::cout << WELCOME_STR << std::endl;
    bool active = true;
    std::string input, cmd;
    int sep_pos;
    while (active) {
        std::getline(std::cin, input);
        sep_pos = input.find(' ');
        cmd = input.substr(0, sep_pos);
        if (cmd=="q" || cmd=="qqq" || cmd=="quit" || cmd=="exit") {
            active = false;
        }
        else if (cmd=="h" || cmd=="help") {
            std::cout << HELP_STR << std::endl;
        }
        else if (cmd=="b" || cmd=="board") {
            this->print();
        }
        else if (cmd=="c" || cmd=="iic" || cmd=="check") {
            // TBA
        }
        else if (cmd=="f" || cmd=="fen") {
            if (input.substr(sep_pos+1, 3) == "get") {
                std::cout << this->get_fen() << std::endl;
            }
            else {
                if (sep_pos == std::string::npos) this->set_fen();
                else this->set_fen(input.substr(sep_pos+1, std::string::npos));
            }
        }
        else if (cmd=="l" || cmd=="slm" || cmd=="legal") {
            // TBA
        }
        else if (cmd=="s" || cmd=="spp" || cmd=="pieces") {
            // TBA
        }
        else if (cmd=="m" || cmd=="mv" || cmd=="move") {
            // TBA
        }
        else if (cmd=="u" || cmd=="um" || cmd=="undo" || cmd=="unmove") {
            // TBA
        }
        else if (cmd=="p" || cmd=="perft") {
            // TBA
        }
        else if (cmd=="d" || cmd=="divide") {
            // TBA
        }
        else {
            std::cout << "Unknown command: " << cmd << std::endl;
        }
    }
}

void Board::_upd_king(const bool white, const int sq_to) {
    if (white) this->w_king_square = sq_to;
    else this->b_king_square = sq_to;
}

void Board::_upd_piece_l(const bool white, const int sq_from, const int sq_to) {
    flInt* p_l = (white) ? &this->w_pcs : &this->b_pcs;
    if (sq_from == -1) {
        p_l->push_front(sq_to); return;
    }
    if (sq_to == -1) {
        p_l->remove(sq_from); return; // suboptimal, TODO: optimise
    }
    for (flInt::iterator p=p_l->begin(); p!=p_l->end(); p++) {
        if (*p == sq_from) {
            *p = sq_to; return;
        }
    }
    std::cerr << "DEBUG: Piece not found in list" << std::endl;
}

void Board::testing() {
    this->print(this->b_pcs);
}

int main() {
    std::ios_base::sync_with_stdio(0);
    std::cin.tie(0);

    std::cout << LOGO_STR << std::endl;
    Board the_board;
    the_board.interactive_mode();

    return 0;
}