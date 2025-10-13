class Knight():
    def __init__(self, board=None):
        self.board = board
    
    def generate_knight_moves(self, is_white, board=None):
        if board:
            self.board = board
        
        moves = []
        knights = self.board.white_knights if is_white else self.board.black_knights
        friendly_pieces = self.board.pieces.get_all_white_pieces() if is_white else self.board.pieces.get_all_black_pieces()
        
        temp_knights = knights

        while temp_knights:
            square = (temp_knights & -temp_knights).bit_length() - 1
            temp_knights &= temp_knights - 1

            row, col = divmod(square, 8)
            from_square = chr(col + ord('a')) + str(row + 1)

            possible_moves = self.board.knight_moves[square] & ~friendly_pieces
            temp_moves = possible_moves

            while temp_moves:
                to_square_bit = (temp_moves & -temp_moves).bit_length() - 1
                temp_moves &= temp_moves - 1

                to_row, to_col = divmod(to_square_bit, 8)
                to_square = chr(to_col + ord('a')) + str(to_row + 1)
                moves.append((from_square, to_square))
                
        
        return moves