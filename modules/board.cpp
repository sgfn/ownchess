#include <chrono>
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
    char from_piece, to_piece;
    int move_type, can_castle, ep_square, hm_clock;
    vPIntInt legal_moves;
};

int alg_to_num(const std::string alg_coords) {
    return ((alg_coords[1]-49)<<3) + alg_coords[0]-97;
}

std::string num_to_alg(const int sq_num) {
    if (sq_num == -1) return "-";
    std::string alg_str = "";
    alg_str.push_back((sq_num&7) + 97);
    alg_str.push_back((sq_num>>3) + 49);
    return alg_str;
}

class Board {
        square chessboard[64];
        bool w_to_move; // true if white to move
        int can_castle, ep_square, hm_clock, fm_counter, w_king_square, b_king_square;
        flInt w_pcs, b_pcs; // piece lists
        vPIntInt _all_legal_moves;
        std::deque<move_record> move_history;
        void _add_piece(const bool, const char, const int);
        pIntInt _move_piece(const int, const int);
        pIntInt _move_piece(const int, const int, const char, const bool);
        void _unmove_piece(const int, const int, const bool, const char, const char);
        void _unmove_piece(const int, const int, const bool, const char, const char, const bool);
        void _upd_king(const bool, const int);
        void _upd_piece_l(const bool, const int, const int);
    public:
        Board(const std::string);
        void print();
        void print(const vPIntInt &, const int);
        void print(const flInt &);
        void print(const usInt &);
        void set_fen(const std::string);
        std::string get_fen();
        vInt get_pseudolegal_moves(const int);
        vPIntInt get_all_pseudolegal_moves();
        bool is_in_check();
        bool is_in_check(const bool);
        vPIntInt get_legal_moves(const int);
        void show_legal_moves(const int);
        void show_piece_positions(const bool);
        vPIntInt get_all_legal_moves();
        void make_move(const int, const int, const char, const bool);
        void unmake_move();
        int detect_game_end(const bool);
        int perft(const int);
        void interactive_mode();
        void testing();
};

Board::Board(const std::string fen = FEN_INIT) {
    this->_all_legal_moves.reserve(218);
    this->set_fen(fen);
}

void Board::print() {
    const usInt empty_set; // disgusting hack, TODO: rewrite
    this->print(empty_set);
}

void Board::print(const vPIntInt &h_sqrs_vp, const int sq_num) {
    usInt h_sqrs_s;
    for (pIntInt pair : h_sqrs_vp) {
        if (pair.first == sq_num) h_sqrs_s.insert(pair.second);
    }
    this->print(h_sqrs_s);
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
                    bool white = (ch >= 65 && ch <= 90); // is ch uppercase
                    int sq_num = ((7-row)<<3) + col++;
                    if (ch=='k' || ch=='K') { // update king squares
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
                this->can_castle = 0;
            }
            else if (fen_field==2) { // set the correct castling rights
                switch (ch) {
                    case 'K': this->can_castle += 8; break;
                    case 'Q': this->can_castle += 4; break;
                    case 'k': this->can_castle += 2; break;
                    case 'q': this->can_castle += 1; break;
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
    // Update list of legal moves
    this->_all_legal_moves = this->get_all_legal_moves();

    // Detect and handle game ending states
    this->detect_game_end(true);
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
    char cn_cs_char[4] = {'K', 'Q', 'k', 'q'};
    int mask = 8;
    for (int i=0; i<4; i++) {
        if (this->can_castle & mask > 0) cn_cs += cn_cs_char[i];
        mask>>=1;
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
            int cs_kside_mask = (from_white) ? 8 : 2;
            square* b = this->chessboard;
            int tmp_iic_val = -1; // helper var for storing is_in_check() result
            if (this->can_castle&cs_kside_mask > 0) { // castling kingside
                for (int i=1; i<3; ++i) {
                    if (b[sq_num+i].colour != 'e') break;
                    if (i == 2) { // TODO: consider rewriting this bit of code
                        tmp_iic_val = (this->is_in_check()) ? 1 : 0;
                        if (tmp_iic_val==0) plegal_moves.push_back(sq_num+2);
                    }
                }
            }
            if (this->can_castle&(cs_kside_mask>>1) > 0) { // castling queenside
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

bool Board::is_in_check(const bool curr_player) { // can be more efficient - don't check the same squares more than once; TODO: rewrite
    const bool w_king = (curr_player) ? this->w_to_move : !this->w_to_move;
    const char opp_clr = (w_king) ? 'b' : 'w';
    const int k_row = (w_king) ? w_king_square>>3 : b_king_square>>3;
    const int k_col = (w_king) ? w_king_square&7 : b_king_square&7; // TODO: consider rewriting
    const int pawn_move = (w_king) ? 1 : -1;
    int atk_row, atk_col;
    square* atk_sq;
    const int mv_col[2] = {-1, 1}; // pawn checks
    for (int i=0; i<2; ++i) {
        atk_row = k_row + pawn_move; atk_col = k_col + mv_col[i];
        if (0<=atk_row && atk_row<=7 && 0<=atk_col && atk_col<=7) {
            atk_sq = &this->chessboard[(atk_row<<3)+atk_col];
            if (atk_sq->piece=='p' && atk_sq->colour==opp_clr) return true;
        }
    }
    vPIntInt moves[2] = {{{1, 1}, {1, 0}, {1, -1}, {0, 1}, 
                          {0, -1}, {-1, 1}, {-1, 0}, {-1, -1}}, 
                         {{1, 2}, {1, -2}, {-1, 2}, {-1, -2}, 
                          {2, 1}, {2, -1}, {-2, 1}, {-2, -1}}};
    char pcs[2] = {'k', 'n'};
    for (int i=0; i<2; ++i) { // kings on adjacent squares, knight checks
        for (pIntInt pair : moves[i]) {
            atk_row = k_row + pair.first; atk_col = k_col + pair.second;
            if (0<=atk_row && atk_row<=7 && 0<=atk_col && atk_col<=7) {
                atk_sq = &this->chessboard[(atk_row<<3)+atk_col];
                if (atk_sq->piece==pcs[i]&&atk_sq->colour==opp_clr) return true;
            }
        }
    }
    vPIntInt ray_moves[2] = {{{-1, -1}, {-1, 1}, {1, -1}, {1, 1}}, 
                         {{-1, 0}, {0, -1}, {1, 0}, {0, 1}}};
    char ray_pcs[2] = {'b', 'r'};
    for (int i=0; i<2; ++i) { // ray piece checks
        for (pIntInt pair : ray_moves[i]) {
            atk_row = k_row + pair.first; atk_col = k_col + pair.second;
            while (0<=atk_row && atk_row<=7 && 0<=atk_col && atk_col<=7) {
                atk_sq = &this->chessboard[(atk_row<<3)+atk_col];
                if ((atk_sq->piece==ray_pcs[i] || atk_sq->piece=='q') && 
                     atk_sq->colour==opp_clr) return true;
                else if (atk_sq->colour != 'e') break;
                atk_row += pair.first; atk_col += pair.second;
            }
        }
    }
    return false;
}

vPIntInt Board::get_legal_moves(const int from_num) {
    vInt plegal_moves = this->get_pseudolegal_moves(from_num);
    vPIntInt legal_moves;
    const square* from_sq = &this->chessboard[from_num];
    const bool from_white = (from_sq->colour == 'w');
    const char opp_colour = (from_white) ? 'b' : 'w';
    const char from_piece = from_sq->piece;
    if (from_white != this->w_to_move)      return legal_moves;
    square* to_sq;
    char to_piece;
    for (int to_num : plegal_moves) {
        to_sq = &this->chessboard[to_num];
        to_piece = to_sq->piece;
        if (from_piece == 'k' && abs(to_num - from_num) == 2) { // castling
            int cs_dir = (to_num > from_num) ? 1 : -1; // determine side
            this->_move_piece(from_num, from_num + cs_dir);
            if (this->is_in_check()) { // illegal if king in check on this sq
                this->_move_piece(from_num + cs_dir, from_num); // maybe should call _unmove_piece()? TODO: consider changing
                continue;
            }
            this->_move_piece(from_num + cs_dir, from_num); // see above
        }
        this->_move_piece(from_num, to_num); // move, see if in check, unmove
        if (!this->is_in_check()) 
            legal_moves.push_back(std::make_pair(from_num, to_num));
        this->_unmove_piece(from_num, to_num, from_white, from_piece, to_piece);
    }
    return legal_moves;
}

void Board::show_legal_moves(const int sq_num) {
    this->print(this->_all_legal_moves, sq_num);
}

void Board::show_piece_positions(const bool curr_player) {
    bool white = (curr_player) ? this->w_to_move : !this->w_to_move;
    flInt* p = (white) ? &this->w_pcs : &this->b_pcs;
    this->print(*p);
}

vPIntInt Board::get_all_legal_moves() {
    vPIntInt all_legal_moves, t;
    const flInt* p = (this->w_to_move) ? &this->w_pcs : &this->b_pcs;
    for (int sq_num : *p) {
        t = this->get_legal_moves(sq_num);
        all_legal_moves.insert(all_legal_moves.end(), t.begin(), t.end());
    }
    return all_legal_moves;
}

void Board::make_move(const int fr_num, const int to_num, 
                      const char promote_to = 'q', const bool perft = false) {
    if (!perft) { // suboptimal, but who cares (not an important part); TODO: maybe fix
        bool is_ok = false;
        for (pIntInt pair : this->_all_legal_moves) {
            if (pair.first == fr_num && pair.second == to_num) {
                is_ok = true; break;
            }
        }
        if (!is_ok) {
            std::cout << "DEBUG: Illegal move" << std::endl; return;
        }
    }
    const int cn_cs = this->can_castle; // store board properties before making the move
    const int ep_sq = this->ep_square;
    const int hm_cl = this->hm_clock;

    const square* fr_sq = &this->chessboard[fr_num];
    const square* to_sq = &this->chessboard[to_num];
    const bool fr_white = (fr_sq->colour == 'w');
    const char fr_piece = fr_sq->piece;
    const char to_piece = to_sq->piece;

    // Detecting loss of castling rights
    // King has moved from the starting square
    if ((fr_num==4||fr_num==60) && fr_piece=='k') {
        this->can_castle &= (fr_white) ? 3 : 12;
    }
    // Rook has moved from the starting square
    else if ((fr_num==0||fr_num==7||fr_num==56||fr_num==63) && fr_piece=='r') {
        if ((fr_num==7&&fr_white) || (fr_num==63&&!fr_white)) {
            this->can_castle &= (fr_white) ? 7 : 13;
        }
        else if ((fr_num==0&&fr_white) || (fr_num==56&&!fr_white)) {
            this->can_castle &= (fr_white) ? 11 : 14;
        }
    }
    // Rook was captured
    else if ((to_num==0||to_num==7||to_num==56||to_num==63) && to_piece=='r') {
        // Capturing the rook removes castling rights for the opponent
        if ((to_num==7&&!fr_white) || (to_num==63&&fr_white)) {
            this->can_castle &= (!fr_white) ? 7  : 13;
        }
        else if ((to_num==0&&!fr_white) || (to_num==56&&fr_white)) {
            this->can_castle &= (!fr_white) ? 11 : 14;
        }
    }

    // Move the piece and check whether to reset the halfmove clock
    pIntInt mp_res = this->_move_piece(fr_num, to_num, promote_to, true);
    if (mp_res.first > 0)   this->hm_clock = 0;
    else                    this->hm_clock++;

    if (!this->w_to_move)   this->fm_counter++;
    this->w_to_move = !this->w_to_move;

    vPIntInt lgl_mvs = {this->_all_legal_moves};

    // Update the move history
    move_record r = {fr_num, to_num, fr_piece, to_piece, mp_res.second, cn_cs, 
                     ep_sq, hm_cl, lgl_mvs};
    this->move_history.push_back(r);

    // Detect possibility of en passant in next ply
    if (fr_piece == 'p') {
        if      (to_num-fr_num ==  16)  this->ep_square = to_num-8;
        else if (to_num-fr_num == -16)  this->ep_square = to_num+8;
        else                            this->ep_square = -1;
    }
    else    this->ep_square = -1;

    // Update the list of legal moves
    this->_all_legal_moves = this->get_all_legal_moves();

    // Detect and handle game ending states
    if (!perft)    this->detect_game_end(true);
}

void Board::unmake_move() {
    if (this->move_history.empty()) {
        std::cerr << "DEBUG: Nothing to unmake" << std::endl;
        return;
    }
    // Get the most recent move record and delete it from the history
    move_record r = this->move_history.back();
    this->move_history.pop_back(); // TODO: maybe rewrite so as not to copy r

    // Reinstate previous board properties
    this->can_castle = r.can_castle;
    this->ep_square = r.ep_square;
    this->hm_clock = r.hm_clock;
    if (this->w_to_move)    this->fm_counter--;

    // Unmake the move
    this->_unmove_piece(r.from_num, r.to_num, !this->w_to_move, r.from_piece, r.to_piece, true);

    // Change the player to move, load the vector of legal moves from cache
    this->w_to_move = !this->w_to_move;
    this->_all_legal_moves = r.legal_moves;
}

int Board::detect_game_end(const bool verbose = false) {
    if (this->_all_legal_moves.empty()) {
        if (this->is_in_check()) {
            if (verbose) {
                std::string clr = (this->w_to_move) ? "Black" : "White";
                std::cout << "Checkmate. " << clr << " wins" << std::endl;
            }
            return 1;
        }
        else {
            if (verbose)    std::cout << "Stalemate" << std::endl;
            return 2;
        }
    }
    return 0;
}

int Board::perft(const int depth) {
    if (depth == 1) {
        int counter = 0;
        for (pIntInt pair : this->_all_legal_moves) {
            if (this->chessboard[pair.first].piece=='p' && (pair.second>>3==0||pair.second>>3==7)) {
                counter += 4;
            }
            else    ++counter;
        }
        return counter;
    }
    else if (depth < 1) {
        if (depth == 0) return 1;
        else            throw std::underflow_error("Negative depth");
    }

    int leaf_nodes = 0;
    vPIntInt alm = {this->_all_legal_moves};
    for (pIntInt pair : alm) {
        // Handling promotions
        if (this->chessboard[pair.first].piece=='p' && (pair.second>>3==0||pair.second>>3==7)) {
            for (char promote_to : {'q', 'r', 'b', 'n'}) {
                this->make_move(pair.first, pair.second, promote_to, true);
                leaf_nodes += this->perft(depth-1);
                this->unmake_move();
            }
        }
        else {
            this->make_move(pair.first, pair.second, 'q', true);
            leaf_nodes += this->perft(depth-1);
            this->unmake_move();
        }
    }
    return leaf_nodes;
}

void Board::interactive_mode() {
    std::cout << WELCOME_STR << std::endl;
    bool active = true;
    std::string input, cmd, args;
    int sep_pos;
    while (active) {
        std::getline(std::cin, input);
        sep_pos = input.find(' ');
        cmd = input.substr(0, sep_pos);
        args = input.substr(sep_pos+1, std::string::npos);
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
            std::cout << this->is_in_check() << std::endl;
        }
        else if (cmd=="f" || cmd=="fen") {
            if (input.substr(sep_pos+1, 3) == "get") {
                std::cout << this->get_fen() << std::endl;
            }
            else {
                if (sep_pos == std::string::npos) this->set_fen();
                else this->set_fen(args);
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
            auto s_tm = std::chrono::high_resolution_clock::now();
            const int nodes = this->perft(std::stoi(args));
            auto e_tm = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double, std::milli> t_tm = e_tm-s_tm;
            std::cout << "Nodes: " << nodes << " \tTime: " << t_tm.count();
            std::cout << " ms" << std::endl;
        }
        else if (cmd=="d" || cmd=="divide") {
            // TBA
        }
        else {
            std::cout << "Unknown command: " << cmd << std::endl;
        }
    }
}

void Board::_add_piece(const bool white, const char piece, const int sq_num) {
    square* to_sq = &this->chessboard[sq_num];

    if (piece == 'k')   this->_upd_king(white, sq_num);

    to_sq->colour = (white) ? 'w' : 'b';
    to_sq->piece = piece;
}

pIntInt Board::_move_piece(const int from_num, const int to_num) {
    return this->_move_piece(from_num, to_num, 'q', false);
}

pIntInt Board::_move_piece(const int from_num, const int to_num, const char promote_to, const bool upd_lists) {
    // std::cout << "MV " << num_to_alg(from_num) << "->" << num_to_alg(to_num) << std::endl;
    int reset_hm_cl = 0, move_type = 's';
    square* from_sq = &this->chessboard[from_num];
    if (from_sq->colour == 'e') {
        std::cerr << "DEBUG: Square " << from_num << " is empty" << std::endl;
        return std::make_pair(0, 0);
    }
    const bool from_white = (from_sq->colour == 'w');
    const char their_colour = (from_white) ? 'b' : 'w';

    if (from_sq->piece == 'k') {
        this->_upd_king(from_white, to_num);
        // Handle castling moves
        if ((from_num==4||from_num==60) && abs(to_num-from_num)==2) {
            move_type = 'c';
            const bool c_kside = (to_num > from_num); // true if kingside
            const int r_from = (c_kside) ? from_num+3 : from_num-4;
            const int r_to   = (c_kside) ? from_num+1 : from_num-1;

            this->chessboard[r_to].colour   = (from_white) ? 'w' : 'b';
            this->chessboard[r_to].piece    = 'r';
            this->chessboard[r_from].colour = 'e';
            this->chessboard[r_from].piece  = 'e';

            if (upd_lists)  this->_upd_piece_l(from_white, r_from, r_to);
        }
    }

    // Standard capture
    if (to_num!=-1 && this->chessboard[to_num].colour==their_colour) {
        reset_hm_cl = 2;

        if (upd_lists)  this->_upd_piece_l(!from_white, to_num, -1);
    }

    if (from_sq->piece == 'p') {
        reset_hm_cl = 1;
        // Handle promotions
        const int pr_row = (from_white) ? 7 : 0;
        if (to_num>>3 == pr_row) {
            move_type = promote_to;
            this->_add_piece(from_white, promote_to, to_num);
        }

        // Handle en passant
        else if (to_num == this->ep_square) {
            move_type = 'e';
            const int ep_pawn_sq = (to_num > from_num) ? to_num-8 : to_num+8;
            this->chessboard[ep_pawn_sq].colour = 'e';
            this->chessboard[ep_pawn_sq].piece = 'e';

            if (upd_lists)  this->_upd_piece_l(!from_white, ep_pawn_sq, -1);
        }
    }

    // Actually move the piece
    if (to_num != -1 && move_type != promote_to) {
        this->chessboard[to_num].colour = (from_white) ? 'w' : 'b';
        this->chessboard[to_num].piece = from_sq->piece;
    }

    from_sq->colour = 'e';
    from_sq->piece = 'e';

    if (upd_lists)  this->_upd_piece_l(from_white, from_num, to_num);

    return std::make_pair(reset_hm_cl, move_type);
}

void Board::_unmove_piece(const int from_num, const int to_num, const bool from_white, const char from_piece, const char to_piece) {
    return this->_unmove_piece(from_num, to_num, from_white, from_piece, to_piece, false);
}

void Board::_unmove_piece(const int from_num, const int to_num, const bool from_white, const char from_piece, const char to_piece, const bool upd_lists) {
    // std::cout << "UMV " << num_to_alg(from_num) << "->" << num_to_alg(to_num) << " fr_wh:" << from_white << "; fr_pc:" << from_piece << "; to_pc:" << to_piece << "; upd_lists:" << upd_lists << std::endl;
    square* from_sq = &this->chessboard[from_num];
    square* to_sq   = &this->chessboard[to_num];

    const char from_colour  = (from_white) ? 'w' : 'b';
    const char their_colour = (from_white) ? 'b' : 'w';

    if (to_piece != 'e') { // Move was a standard capture
        from_sq->colour = from_colour;
        from_sq->piece = from_piece;
        to_sq->colour = their_colour;
        to_sq->piece = to_piece;

        if (upd_lists)  this->_upd_piece_l(!from_white, -1, to_num);
    }
    else { // Move was either en passant or not a capture (possibly castling)
        // Handle en passant
        if (from_piece == 'p' && to_num == this->ep_square) {
            const int ep_pawn_sq = (to_num > from_num) ? to_num-8 : to_num+8;
            this->chessboard[ep_pawn_sq].colour = their_colour;
            this->chessboard[ep_pawn_sq].piece = 'p';

            if (upd_lists)  this->_upd_piece_l(!from_white, -1, ep_pawn_sq);
        }
        // Handle castling
        else if (from_piece == 'k' && abs(to_num-from_num) == 2) {
            const bool c_kside = (to_num > from_num); // true if kingside
            const int r_from = (c_kside) ? from_num+3 : from_num-4;
            const int r_to   = (c_kside) ? from_num+1 : from_num-1;

            this->chessboard[r_to].colour   = 'e';
            this->chessboard[r_to].piece    = 'e';
            this->chessboard[r_from].colour = from_colour;
            this->chessboard[r_from].piece  = 'r';

            if (upd_lists)  this->_upd_piece_l(from_white, r_to, r_from);
        }
        this->_move_piece(to_num, from_num, 'q', false);
    }

    if (upd_lists)  this->_upd_piece_l(from_white, to_num, from_num);

    // Cleaning up after unmaking a promotion
    if (from_piece != from_sq->piece)   from_sq->piece = from_piece;

    // Update king position
    if (from_piece == 'k')  this->_upd_king(from_white, from_num);
}

void Board::_upd_king(const bool white, const int sq_to) {
    // std::cout << "UPD KING " << white << sq_to << std::endl;
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
    this->print(this->w_pcs);
    // int i = 0;
    // for (square s : this->chessboard) {
    //     std::cout << i++ << ' ' << s.colour << ' ' << s.piece << std::endl;
    // }
}

int main() {
    std::ios_base::sync_with_stdio(0);
    std::cin.tie(0);

    std::cout << LOGO_STR << std::endl;
    Board the_board;
    // the_board.testing();
    the_board.interactive_mode();

    return 0;
}