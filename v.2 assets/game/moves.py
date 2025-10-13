from chesspieces.pawns import Pawn
from chesspieces.knights import Knight
from chesspieces.bishops import Bishop
from chesspieces.rooks import Rook
from chesspieces.queens import Queen

class moves():
    def __init__(self, board):
        self.board = board
        self.pieces = board.pieces

        self.pawns = Pawn(self.board)
        self.knights = Knight(self.board)
        self.bishops = Bishop(self.board)
        self.rooks = Rook(self.board)
        self.queens = Queen(self.board)
        

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
        

    def generate_piece_moves(self, piece_type, is_white):
        moves = []

        if piece_type == 'pawn':
            return self.pawns.generate_pawn_moves(is_white)
        
        if piece_type == 'knight':
            return self.knights.generate_knight_moves(is_white)
        
        if piece_type == 'bishop':
            return self.bishops.generate_bishop_moves(is_white)
        
        if piece_type == 'rook':
            return self.rooks.generate_rook_moves(is_white)
        
        if piece_type == 'queen': 
            return self.queens.generate_queen_moves(is_white)

        if piece_type == 'king':
            pieces = self.board.white_king if is_white else self.board.black_king
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
        is_white = self.board.white_to_move
        moves = []
        
        moves.extend(self.generate_piece_moves('pawn', is_white))
        moves.extend(self.generate_piece_moves('king', is_white))
        moves.extend(self.generate_piece_moves('knight', is_white))
        moves.extend(self.generate_piece_moves('bishop', is_white))
        moves.extend(self.generate_piece_moves('rook', is_white))
        moves.extend(self.generate_piece_moves('queen', is_white))
        
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


        is_king_in_check = self.is_king_in_check(not self.board.white_to_move)
        
        return True
    

    def is_move_legal(self, from_square, to_square):
        """Check if a move is legal (doesn't leave own king in check)"""
        # Save current board state
        original_board_state = self.save_board_state()
        
        # Make the move temporarily
        move_successful = self.make_move(from_square, to_square)
        if not move_successful:
            return False
        
        # Check if our own king is now in check (which would make the move illegal)
        # Note: after make_move, the turn has switched, so we check the previous player's king
        previous_player_was_white = not self.board.white_to_move
        king_in_check = self.is_king_in_check(previous_player_was_white)
        
        # Restore original board state
        self.restore_board_state(original_board_state)
        
        # Move is legal if it doesn't leave our king in check
        return not king_in_check
    
    def save_board_state(self):
        """Save the current board state"""
        return {
            'white_pawns': self.board.white_pawns,
            'white_rooks': self.board.white_rooks,
            'white_knights': self.board.white_knights,
            'white_bishops': self.board.white_bishops,
            'white_queen': self.board.white_queen,
            'white_king': self.board.white_king,
            'black_pawns': self.board.black_pawns,
            'black_rooks': self.board.black_rooks,
            'black_knights': self.board.black_knights,
            'black_bishops': self.board.black_bishops,
            'black_queen': self.board.black_queen,
            'black_king': self.board.black_king,
            'white_to_move': self.board.white_to_move,
            'en_passant_target': self.board.en_passant_target,
            'move_count': self.board.move_count
        }
    
    def restore_board_state(self, state):
        """Restore a previously saved board state"""
        self.board.white_pawns = state['white_pawns']
        self.board.white_rooks = state['white_rooks']
        self.board.white_knights = state['white_knights']
        self.board.white_bishops = state['white_bishops']
        self.board.white_queen = state['white_queen']
        self.board.white_king = state['white_king']
        self.board.black_pawns = state['black_pawns']
        self.board.black_rooks = state['black_rooks']
        self.board.black_knights = state['black_knights']
        self.board.black_bishops = state['black_bishops']
        self.board.black_queen = state['black_queen']
        self.board.black_king = state['black_king']
        self.board.white_to_move = state['white_to_move']
        self.board.en_passant_target = state['en_passant_target']
        self.board.move_count = state['move_count']

    def is_king_in_check(self, is_white):
        king_bitboard = self.board.white_king if is_white else self.board.black_king
        if king_bitboard == 0:
            return False 
        
        king_square = (king_bitboard & -king_bitboard).bit_length() - 1
        opponent_is_white = not is_white

        opponent_attacks = self.generate_attack_map(opponent_is_white)
        return (opponent_attacks & king_bitboard) != 0
    
    def generate_attack_map(self, is_white):
        attacks = 0
        all_pieces = self.board.pieces.get_all_pieces()
        
        # Knight attacks
        temp_knights = self.board.white_knights if is_white else self.board.black_knights
        while temp_knights:
            square = (temp_knights & -temp_knights).bit_length() - 1
            temp_knights &= temp_knights - 1
            attacks |= self.board.knight_moves[square]

        # King attacks
        king_bitboard = self.board.white_king if is_white else self.board.black_king
        if king_bitboard:
            square = (king_bitboard & -king_bitboard).bit_length() - 1
            attacks |= self.board.king_moves[square]

        # Bishop attacks
        temp_bishops = self.board.white_bishops if is_white else self.board.black_bishops
        while temp_bishops:
            square = (temp_bishops & -temp_bishops).bit_length() - 1
            temp_bishops &= temp_bishops - 1
            row, col = divmod(square, 8)
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 8 and 0 <= new_col < 8:
                    to_pos = new_row * 8 + new_col
                    attacks |= 1 << to_pos
                    
                    # Stop if there's a piece blocking the path
                    if all_pieces & (1 << to_pos):
                        break
                        
                    new_row += dr
                    new_col += dc

        # Rook attacks
        temp_rooks = self.board.white_rooks if is_white else self.board.black_rooks
        while temp_rooks:
            square = (temp_rooks & -temp_rooks).bit_length() - 1
            temp_rooks &= temp_rooks - 1
            row, col = divmod(square, 8)
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 8 and 0 <= new_col < 8:
                    to_pos = new_row * 8 + new_col
                    attacks |= 1 << to_pos
                    
                    # Stop if there's a piece blocking the path
                    if all_pieces & (1 << to_pos):
                        break
                        
                    new_row += dr
                    new_col += dc

        # Queen attacks (combination of bishop and rook)
        temp_queens = self.board.white_queen if is_white else self.board.black_queen
        while temp_queens:
            square = (temp_queens & -temp_queens).bit_length() - 1
            temp_queens &= temp_queens - 1
            row, col = divmod(square, 8)
            
            # Bishop-like moves for queen
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 8 and 0 <= new_col < 8:
                    to_pos = new_row * 8 + new_col
                    attacks |= 1 << to_pos
                    
                    if all_pieces & (1 << to_pos):
                        break
                        
                    new_row += dr
                    new_col += dc
            
            # Rook-like moves for queen
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                while 0 <= new_row < 8 and 0 <= new_col < 8:
                    to_pos = new_row * 8 + new_col
                    attacks |= 1 << to_pos
                    
                    if all_pieces & (1 << to_pos):
                        break
                        
                    new_row += dr
                    new_col += dc

        # Pawn attacks
        temp_pawns = self.board.white_pawns if is_white else self.board.black_pawns
        while temp_pawns:
            square = (temp_pawns & -temp_pawns).bit_length() - 1
            temp_pawns &= temp_pawns - 1
            row, col = divmod(square, 8)
            if is_white:
                for dc in [-1, 1]:
                    to_row, to_col = row + 1, col + dc
                    if 0 <= to_row < 8 and 0 <= to_col < 8:
                        attacks |= 1 << (to_row * 8 + to_col)
            else:
                for dc in [-1, 1]:
                    to_row, to_col = row - 1, col + dc
                    if 0 <= to_row < 8 and 0 <= to_col < 8:
                        attacks |= 1 << (to_row * 8 + to_col)

        return attacks
