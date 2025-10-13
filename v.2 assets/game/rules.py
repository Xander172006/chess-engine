from pieces import pieces

class rules():
    def __init__(self, board=None):
        self.board = board
        self.pieces = pieces(board) if board else None

    def is_valid_square(self, square_name):
        if len(square_name) != 2:
            return False
        return 'a' <= square_name[0] <= 'h' and '1' <= square_name[1] <= '8'
    
    def is_checkmate(self):
        return self.board.white_king == 0 or self.board.black_king == 0
    
    def get_winner(self):
        if self.board.white_king == 0:
            return 'Black'
        elif self.board.black_king == 0:
            return 'White'
        return None