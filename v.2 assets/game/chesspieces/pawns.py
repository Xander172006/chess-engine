class Pawn():
        def __init__(self, board=None):
           self.board = board
           

        def generate_pawn_moves(self, is_white):
            moves = []
            # get all pawns
            pawns = self.board.white_pawns if is_white else self.board.black_pawns
            all_pieces = self.board.pieces.get_all_pieces()
            enemy_pieces = self.board.pieces.get_all_black_pieces() if is_white else self.board.pieces.get_all_white_pieces()

            # determine move direction
            direction = 1 if is_white else -1
            start_rank = 1 if is_white else 6

            temp_pawns = pawns

            # simulate moves for each pawn
            while temp_pawns:
                # find least significant bit (LSB)
                square = (temp_pawns & -temp_pawns).bit_length() - 1
                temp_pawns &= temp_pawns - 1

                # get to and from squares
                row, col = divmod(square, 8)
                from_square = chr(col + ord('a')) + str(row + 1)

                new_row = row + direction
                if 0 <= new_row < 8:
                    to_pos =  new_row * 8 + col
                    if not (all_pieces & (1 << to_pos)): # square empty
                        to_square = chr(ord('a') + col) + str(new_row + 1)
                        moves.append((from_square, to_square))

                        if row == start_rank:
                            new_row2 = row + 2 * direction
                            if 0 <= new_row2 < 8:
                                to_pos2 = new_row2 * 8 + col
                                if not (all_pieces & (1 << to_pos2)):
                                    to_square2 = chr(ord('a') + col) + str(new_row2 + 1)
                                    moves.append((from_square, to_square2))


                # Captures
                for dc in [-1, 1]:
                    new_col = col + dc
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        to_pos = new_row * 8 + new_col
                        if (enemy_pieces & (1 << to_pos)):
                            to_square = chr(ord('a') + new_col) + str(new_row + 1)
                            moves.append((from_square, to_square))

            return moves