class Rook():
    def __init__(self, board):
        self.board = board

    def generate_rook_moves(self, is_white):
        moves = []

        rooks = self.board.white_rooks if is_white else self.board.black_rooks
        all_pieces = self.board.pieces.get_all_pieces()
        enemy_pieces = self.board.pieces.get_all_black_pieces() if is_white else self.board.pieces.get_all_white_pieces()

        temp_rooks = rooks

        while temp_rooks:
            square = (temp_rooks & -temp_rooks).bit_length() - 1
            temp_rooks &= temp_rooks - 1
            
            row, col = divmod(square, 8)
            from_square = chr(col + ord('a')) + str(row + 1)
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

            for dr, dc in directions:
                for distance in range(1, 8):
                    to_row = row + dr * distance
                    to_col = col + dc * distance
                    if 0 <= to_row < 8 and 0 <= to_col < 8:
                        to_square = chr(to_col + ord('a')) + str(to_row + 1)
                        to_square_bit = 1 << (to_row * 8 + to_col)
                        if all_pieces & to_square_bit:
                            if enemy_pieces & to_square_bit:
                                moves.append((from_square, to_square))
                            break
                        else:
                            moves.append((from_square, to_square))
                    else:
                        break

        return moves