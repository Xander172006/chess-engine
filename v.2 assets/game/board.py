from pieces import pieces
from colorama import Fore, Style

class board():
    def __init__(self):
        self.white_pawns = 0x000000000000FF00
        self.white_rooks = 0x0000000000000081 
        self.white_knights = 0x0000000000000042 
        self.white_bishops = 0x0000000000000024 
        self.white_queen = 0x0000000000000008
        self.white_king = 0x0000000000000010
        
        self.black_pawns = 0x00FF000000000000
        self.black_rooks = 0x8100000000000000
        self.black_knights = 0x4200000000000000
        self.black_bishops = 0x2400000000000000
        self.black_queen = 0x0800000000000000
        self.black_king = 0x1000000000000000

        self.white_to_move = True
        self.en_passant_target = None
        self.move_count = 0

        self.pieces = pieces(self)

        self.king_moves = [0] * 64
        self.knight_moves = [0] * 64
        self._precompute_moves()
    
    def _precompute_moves(self):
        """Pre-compute king and knight move patterns"""
        for square in range(64):
            row, col = divmod(square, 8)
            king_mask = 0

            # determine king moves in all 8 directions
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 8 and 0 <= new_col < 8:

                        king_mask |= 1 << (new_row * 8 + new_col)
            self.king_moves[square] = king_mask

            # determine knight moves in "L" shapes
            knight_mask = 0
            knight_deltas = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
            for dr, dc in knight_deltas:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    knight_mask |= 1 << (new_row * 8 + new_col)
            self.knight_moves[square] = knight_mask


    def get_piece_at_square(self, square_name):
        bitboard = self.pieces.square_to_bitboard(square_name)

        if self.white_pawns & bitboard: return 'P'
        if self.white_rooks & bitboard: return 'R'
        if self.white_knights & bitboard: return 'N'
        if self.white_bishops & bitboard: return 'B'
        if self.white_queen & bitboard: return 'Q'
        if self.white_king & bitboard: return 'K'
        if self.black_pawns & bitboard: return 'p'
        if self.black_rooks & bitboard: return 'r'
        if self.black_knights & bitboard: return 'n'
        if self.black_bishops & bitboard: return 'b'
        if self.black_queen & bitboard: return 'q'
        if self.black_king & bitboard: return 'k'
        return '.'
    

    def get_piece_symbol_at_square(self, square_name):
        bitboard = self.pieces.square_to_bitboard(square_name)

        if self.white_pawns & bitboard: return '♙'
        if self.white_rooks & bitboard: return '♖'
        if self.white_knights & bitboard: return '♘'
        if self.white_bishops & bitboard: return '♗'
        if self.white_queen & bitboard: return '♕'
        if self.white_king & bitboard: return '♔'
        if self.black_pawns & bitboard: return '♟'
        if self.black_rooks & bitboard: return '♜'
        if self.black_knights & bitboard: return '♞'
        if self.black_bishops & bitboard: return '♝'
        if self.black_queen & bitboard: return '♛'
        if self.black_king & bitboard: return '♚'
        return '.'
    
    def print_board(self, highlight_moves=False):
        possible_moves = set()

        # allow highlights to be on
        if highlight_moves:
            from moves import moves
            move_generator = moves(self)
            all_moves = move_generator.generate_all_moves()
            
            for move in all_moves:
                if isinstance(move, tuple) and len(move) == 2:
                    possible_moves.add(move[1]) 




        print("\n  a b c d e f g h")
        for row in range(7, -1, -1):
            print(f"{row+1} ", end='')
            for col in range(8):
                square_name = chr(col + ord('a')) + str(row + 1)
                piece = self.get_piece_symbol_at_square(square_name) 

                if highlight_moves and square_name in possible_moves:
                    print(Fore.RED + piece + Style.RESET_ALL + " ", end='')
                else:
                    print(piece + " ", end='')
            print(f"{row+1}")
        print("  a b c d e f g h")

        # display turn info
        player = "White" if self.white_to_move else "Black"
        print(f"\nMove {self.move_count + 1}: {player} to move")
        if self.en_passant_target:
            print(f"En Passant Target: {self.en_passant_target}")

        if highlight_moves:
            print(f"{Fore.RED}Red squares{Style.RESET_ALL} show possible moves for {player}")