from devTools import devTools


# create the same code logic as above but with object-oriented programming
class MovesGeneration:
    def __init__(self):
        self.moves = {}
        self.pawn_moved_2_steps = 0


    def generate_all_moves(self, pieces, occupied, color):
        enemy_color = "black" if color == "white" else "white"
        enemy_pieces = (pieces[f"{enemy_color}_pawns"] | pieces[f"{enemy_color}_knights"] | 
                        pieces[f"{enemy_color}_bishops"] | pieces[f"{enemy_color}_rooks"] | 
                        pieces[f"{enemy_color}_queen"] | pieces[f"{enemy_color}_king"])
        
        self.moves['pawns'] = self.generate_pawn_moves(pieces['pawns'], occupied, enemy_pieces, color)
        self.moves['knights'] = self.generate_knight_moves(pieces['knights'], occupied, enemy_pieces)
        self.moves['bishops'] = self.generate_bishop_moves(devTools().from_bitboard_to_chess_position(pieces['bishops']), occupied, enemy_pieces)
        self.moves['rooks'] = self.generate_rook_moves(devTools().from_bitboard_to_chess_position(pieces['rooks']), occupied, enemy_pieces)
        self.moves['queen'] = self.generate_queen_moves(devTools().from_bitboard_to_chess_position(pieces['queen']), occupied, enemy_pieces)
        self.moves['king'] = self.generate_king_moves(devTools().from_bitboard_to_chess_position(pieces['king']), occupied, enemy_pieces)

        return self.moves
    

    def generate_pawn_moves(self, pawns, occupied, enemy_pieces, color):
        # moveset: move 1 or 2 squares forward, capture diagonally
        moves = 0

        if color == "white":
            single_step = (pawns << 8) & ~occupied
            double_step = ((single_step & 0x0000000000FF0000) << 8) & ~occupied
            capture_left = (pawns << 7) & enemy_pieces & ~0x0101010101010101
            capture_right = (pawns << 9) & enemy_pieces & ~0x8080808080808080

        elif color == "black":
            single_step = (pawns >> 8) & ~occupied
            double_step = ((single_step & 0x0000FF0000000000) >> 8) & ~occupied
            capture_left = (pawns >> 9) & enemy_pieces & ~0x0101010101010101
            capture_right = (pawns >> 7) & enemy_pieces & ~0x8080808080808080

        self.pawn_moved_2_steps = double_step

        moves |= single_step | double_step | capture_left | capture_right
        return moves



    # knight moves
    def generate_knight_moves(self, knights, occupied, enemy_pieces):
        # moveset: move in L shapes
        moves = 0
        knight_pos = knights.bit_length() - 1

        knight_moves = [-17, -15, -10, -6, 6, 10, 15, 17]

        for move in knight_moves:
            target_square = knight_pos + move

            # gvie current and target file
            current_file = knight_pos % 8
            target_file = target_square % 8

            # validate move between boundaries
            if 0 <= target_square < 64 and abs(current_file - target_file) <= 2:
                moves |= 1 << target_square

        return moves & ~(occupied & ~enemy_pieces)



    # bishop moves
    def generate_bishop_moves(self, bishops, occupied, enemy_pieces):
        # moveset: move diagonally across the board
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        legal_moves = 0
        start_row, start_col = bishops

        for direction in directions:
            row_offset, col_offset = direction
            current_row, current_col = start_row, start_col

            while True:
                current_row += row_offset
                current_col += col_offset

                if current_row < 0 or current_row >= 8 or current_col < 0 or current_col >= 8:
                    break

                piece = 1 << (current_row * 8 + current_col)
                if piece & occupied:
                    if piece & enemy_pieces:
                        legal_moves |= piece
                    break
                
                legal_moves |= piece

        return legal_moves



    # rook moves
    def generate_rook_moves(self, rook, occupied, enemy_pieces):
        # moveset: move horizontally and vertically
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        legal_moves = 0
        start_row, start_col = rook

        for direction in directions:
            row_offset, col_offset = direction
            current_row, current_col = start_row, start_col

            while True:
                current_row += row_offset
                current_col += col_offset

                if current_row < 0 or current_row >= 8 or current_col < 0 or current_col >= 8:
                    break

                piece = 1 << (current_row * 8 + current_col)
                if piece & occupied:
                    if piece & enemy_pieces:
                        legal_moves |= piece
                    break
                
                legal_moves |= piece

        return legal_moves



    # queen moves
    def generate_queen_moves(self, queen, occupied, enemy_pieces):
        # moveset: move diagonally, horizontally and vertically
        return self.generate_bishop_moves(queen, occupied, enemy_pieces) | self.generate_rook_moves(queen, occupied, enemy_pieces)



    # king moves
    def generate_king_moves(self, king, occupied, enemy_pieces):
        # moveset: move 1 square in any direction
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        legal_moves = 0
        start_row, start_col = king

        for direction in directions:
            row_offset, col_offset = direction
            current_row, current_col = start_row + row_offset, start_col + col_offset

            if current_row < 0 or current_row >= 8 or current_col < 0 or current_col >= 8:
                continue

            piece = 1 << (current_row * 8 + current_col)
            if not piece & occupied:
                legal_moves |= piece

        return legal_moves