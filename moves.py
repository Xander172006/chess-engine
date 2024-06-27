from app import shift_bitboard, FULL_BOARD
from bitboard import print_bitboard


# generates all possible moves on the board
def generate_all_moves(pieces, occupied, color, full_board):
    moves = {}

    # generate enemy pieces
    if color == "white":
        enemy_pieces = pieces['black_pawns'] | pieces['black_knights'] | pieces['black_bishops'] | pieces['black_rooks'] | pieces['black_queen'] | pieces['black_king']
    elif color == "black":
        enemy_pieces = pieces['white_pawns'] | pieces['white_knights'] | pieces['white_bishops'] | pieces['white_rooks'] | pieces['white_queen'] | pieces['white_king']  

    moves['pawns'] = generate_pawn_moves(pieces['pawns'], occupied, enemy_pieces, color)
    moves['knights'] = generate_knight_moves(pieces['knights'], occupied, color)
    moves['bishops'] = generate_bishop_moves(pieces['bishops'], occupied, color)
    moves['rooks'] = generate_rook_moves(pieces['rooks'], occupied, color)
    moves['queen'] = generate_queen_moves(pieces['queen'], occupied, color)
    moves['king'] = generate_king_moves(pieces['king'], occupied, color)

    return moves


# moves for the pawns
def generate_pawn_moves(pawns, occupied, enemy_pieces, color):
    moves = 0

    if color == "white":
        single_step = (pawns << 8) & ~occupied
        double_step = ((single_step & 0x0000000000FF0000) << 8) & ~occupied

        # captures
        capture_left = (pawns << 7) & enemy_pieces & ~0x0101010101010101
        capture_right = (pawns << 9) & enemy_pieces & ~0x8080808080808080

    elif color == "black":
        single_step = (pawns >> 8) & ~occupied
        double_step = ((single_step & 0x0000FF0000000000) >> 8) & ~occupied

        # captures
        capture_left = (pawns >> 9) & enemy_pieces & ~0x0101010101010101
        capture_right = (pawns >> 7) & enemy_pieces & ~0x8080808080808080

    moves |= single_step | double_step | capture_left | capture_right
    return moves




# moves for the knights
def generate_knight_moves(knights, occupied, color):
    moves = 0
    for shift in [-17, -15, -10, -6, 6, 10, 15, 17]:
        moves |= shift_bitboard(knights, shift)
    
    return moves & ~occupied


# moves for the bishops
def generate_bishop_moves(bishops, occupied, color):
    bishop_moves = 0
    for shift in [-9, -7, 7, 9]:
        # generate moves for each direction
        ray = shift_bitboard(bishops, shift)
        while ray:
            # multiply and combine moves
            bishop_moves |= ray
            ray &= ~occupied
            ray = shift_bitboard(ray, shift)
    return bishop_moves & ~occupied


# moves for the rooks
def generate_rook_moves(rooks, occupied, color):
    rook_moves = 0
    for shift in [-8, -1, 1, 8]:
        # generate moves for each direction
        ray = shift_bitboard(rooks, shift)
        while ray:
            # multiply and combine moves
            rook_moves |= ray
            ray &= ~occupied
            ray = shift_bitboard(ray, shift)
    return rook_moves & ~occupied


# moves for the queens
def generate_queen_moves(queens, occupied, color):
    # combine bishop with rook lol :)
    return generate_bishop_moves(queens, occupied, color) | generate_rook_moves(queens, occupied, color)


# moves for the kings
def generate_king_moves(king, occupied, color):
    moves = 0
    # moves 1 square in all directions
    for shift in [-9, -8, -7, -1, 1, 7, 8, 9]:
        moves |= shift_bitboard(king, shift)
    return moves & ~occupied
