class pieces():
    def __init__(self, board=None):
        self.board = board

    def get_all_white_pieces(self):
        if not self.board:
            return 0
        return (self.board.white_pawns | self.board.white_rooks | self.board.white_knights |
                self.board.white_bishops | self.board.white_queen | self.board.white_king)
    
    def get_all_black_pieces(self):
        if not self.board:
            return 0
        return (self.board.black_pawns | self.board.black_rooks | self.board.black_knights |
                self.board.black_bishops | self.board.black_queen | self.board.black_king)
    
    def get_all_pieces(self):
        return self.get_all_white_pieces() | self.get_all_black_pieces()
    
    def square_to_bitboard(self, square_name):
        col = ord(square_name[0]) - ord('a')
        row = int(square_name[1]) - 1
        return 1 << (row * 8 + col)
    
    def bitboard_to_square(self, bitboard):
        if bitboard == 0 or (bitboard & (bitboard - 1)) != 0:
            return None
        square = (bitboard & -bitboard).bit_length() - 1
        row, col = divmod(square, 8)
        return chr(col + ord('a')) + str(row + 1)   