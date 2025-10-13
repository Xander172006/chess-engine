class Bishop():
    def __init__(self, board=None):
        self.board = board

    
    def generate_bishop_moves(self, is_white):
        moves = []

        bishops = self.board.white_bishops if is_white else self.board.black_bishops
        all_pieces = self.board.pieces.get_all_pieces()
        enemy_pieces = self.board.pieces.get_all_black_pieces() if is_white else self.board.pieces.get_all_white_pieces()

        # Generate moves for each bishop
        temp_bishops = bishops

        while temp_bishops:
            square = (temp_bishops & -temp_bishops).bit_length() - 1
            temp_bishops &= temp_bishops - 1

            row, col = divmod(square, 8)
            from_square = chr(col + ord('a')) + str(row + 1)
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 8 and 0 <= new_col < 8:
                    to_pos = new_row * 8 + new_col
                    to_square = chr(ord('a') + new_col) + str(new_row + 1)

                    # capture on enemy piece or stop if blocked by friendly piece
                    if all_pieces & (1 << to_pos):
                        if enemy_pieces & (1 << to_pos): 
                            moves.append((from_square, to_square))
                        break 

                    moves.append((from_square, to_square))
                    new_row += dr
                    new_col += dc

        return moves