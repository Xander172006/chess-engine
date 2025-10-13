from colorama import Fore, Style

class moves():
    def __init__(self, board):
        self.board = board
        self.pieces = board.pieces
        for square in range(64):
            row, col = divmod(square, 8)
            king_mask = 0

            # king
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        king_mask |= 1 << (new_row * 8 + new_col)
            self.board.king_moves[square] = king_mask

            # knight
            knight_mask = 0
            knight_deltas = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
            for dr, dc in knight_deltas:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    knight_mask |= 1 << (new_row * 8 + new_col)
            self.board.knight_moves[square] = knight_mask

            # Note: Rook, Bishop, and Queen moves are not precomputed in this simple version


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
    

    def generate_piece_moves(self, piece_type, is_white):
        moves = []

        if piece_type == 'pawn':
            return self.generate_pawn_moves(is_white)
        
        if piece_type == 'king':
            pieces = self.board.white_king if is_white else self.board.black_king
        elif piece_type == 'knight':
            pieces = self.board.white_knights if is_white else self.board.black_knights
        else:
            return moves
        
        friendly_pieces = self.pieces.get_all_white_pieces() if is_white else self.pieces.get_all_black_pieces()

        temp_pieces = pieces
        while temp_pieces:
            square = (temp_pieces & -temp_pieces).bit_length() - 1
            temp_pieces &= temp_pieces - 1
            
            row, col = divmod(square, 8)
            from_square = chr(ord('a') + col) + str(row + 1)
            
            # Get possible moves for this piece
            if piece_type == 'king':
                possible_moves = self.board.king_moves[square]
            elif piece_type == 'knight':
                possible_moves = self.board.knight_moves[square]
            
            # Filter out moves to squares occupied by friendly pieces
            possible_moves &= ~friendly_pieces
            
            # Convert bitboard moves to square names
            temp_moves = possible_moves
            while temp_moves:
                to_square_bit = (temp_moves & -temp_moves).bit_length() - 1
                temp_moves &= temp_moves - 1
                
                to_row, to_col = divmod(to_square_bit, 8)
                to_square = chr(ord('a') + to_col) + str(to_row + 1)
                moves.append((from_square, to_square))
        
        return moves
    

    def generate_all_moves(self):
        """Generate all legal moves for the current player"""
        is_white = self.board.white_to_move
        moves = []
        
        moves.extend(self.generate_piece_moves('pawn', is_white))
        moves.extend(self.generate_piece_moves('king', is_white))
        moves.extend(self.generate_piece_moves('knight', is_white))
        
        return moves


    def make_move(self, from_square, to_square):
        """Make a move on the board"""
        from_bit = self.pieces.square_to_bitboard(from_square)
        to_bit = self.pieces.square_to_bitboard(to_square)
        
        # Find which piece is moving
        piece = self.board.get_piece_at_square(from_square)
        if piece == '.':
            return False
        
        is_white_piece = piece.isupper()
        
        # Check if it's the correct player's turn
        if is_white_piece != self.board.white_to_move:
            return False
        
        # Remove piece from original position and place at destination
        if piece.upper() == 'P':
            if is_white_piece:
                self.board.white_pawns &= ~from_bit
                self.board.white_pawns |= to_bit
            else:
                self.board.black_pawns &= ~from_bit
                self.board.black_pawns |= to_bit
        elif piece.upper() == 'R':
            if is_white_piece:
                self.board.white_rooks &= ~from_bit
                self.board.white_rooks |= to_bit
            else:
                self.board.black_rooks &= ~from_bit
                self.board.black_rooks |= to_bit
        elif piece.upper() == 'N':
            if is_white_piece:
                self.board.white_knights &= ~from_bit
                self.board.white_knights |= to_bit
            else:
                self.board.black_knights &= ~from_bit
                self.board.black_knights |= to_bit
        elif piece.upper() == 'B':
            if is_white_piece:
                self.board.white_bishops &= ~from_bit
                self.board.white_bishops |= to_bit
            else:
                self.board.black_bishops &= ~from_bit
                self.board.black_bishops |= to_bit
        elif piece.upper() == 'Q':
            if is_white_piece:
                self.board.white_queen &= ~from_bit
                self.board.white_queen |= to_bit
            else:
                self.board.black_queen &= ~from_bit
                self.board.black_queen |= to_bit
        elif piece.upper() == 'K':
            if is_white_piece:
                self.board.white_king &= ~from_bit
                self.board.white_king |= to_bit
            else:
                self.board.black_king &= ~from_bit
                self.board.black_king |= to_bit


        # Remove any captured piece
        self.board.white_pawns &= ~to_bit
        self.board.white_rooks &= ~to_bit
        self.board.white_knights &= ~to_bit
        self.board.white_bishops &= ~to_bit
        self.board.white_queen &= ~to_bit
        self.board.black_pawns &= ~to_bit
        self.board.black_rooks &= ~to_bit
        self.board.black_knights &= ~to_bit
        self.board.black_bishops &= ~to_bit
        self.board.black_queen &= ~to_bit
        
        # Re-add the moving piece (in case we accidentally removed it above)
        if piece.upper() == 'P':
            if is_white_piece:
                self.board.white_pawns |= to_bit
            else:
                self.board.black_pawns |= to_bit
        elif piece.upper() == 'R':
            if is_white_piece:
                self.board.white_rooks |= to_bit
            else:
                self.board.black_rooks |= to_bit
        elif piece.upper() == 'N':
            if is_white_piece:
                self.board.white_knights |= to_bit
            else:
                self.board.black_knights |= to_bit
        elif piece.upper() == 'B':
            if is_white_piece:
                self.board.white_bishops |= to_bit
            else:
                self.board.black_bishops |= to_bit
        elif piece.upper() == 'Q':
            if is_white_piece:
                self.board.white_queen |= to_bit
            else:
                self.board.black_queen |= to_bit
        elif piece.upper() == 'K':
            if is_white_piece:
                self.board.white_king |= to_bit
            else:
                self.board.black_king |= to_bit
        
        # Switch turns
        self.board.white_to_move = not self.board.white_to_move
        if self.board.white_to_move:
            self.board.move_count += 1
        
        return True