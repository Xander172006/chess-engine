WHITE_PAWNS = 0x000000000000FF00
WHITE_KNIGHTS = 0x0000000000000042
WHITE_BISHOPS = 0x0000000000000024
WHITE_ROOKS = 0x0000000000000081
WHITE_QUEEN = 0x0000000000000008
WHITE_KING = 0x0000000000000010

BLACK_PAWNS = 0x00FF000000000000
BLACK_KNIGHTS = 0x4200000000000000
BLACK_BISHOPS = 0x2400000000000000
BLACK_ROOKS = 0x8100000000000000
BLACK_QUEEN = 0x0800000000000000
BLACK_KING = 0x1000000000000000

def create_bitboard(square):
    file = ord(square[0]) - ord('a')
    rank = int(square[1]) - 1
    return 1 << (rank * 8 + file)

def bitboard_to_array(bitboard):
    array = [[0 for _ in range(8)] for _ in range(8)]
    for row in range(8):
        for col in range(8):
            if (bitboard >> (row * 8 + col)) & 1:
                array[7 - row][col] = 1
    return array

def print_bitboard(bitboard):
    board = bitboard_to_array(bitboard)
    for row in board:
        print(" ".join(str(cell) for cell in row))

def generate_knight_moves(knights, occupied, enemy_pieces):
    moves = 0
    knight_pos = knights.bit_length() - 1

    knight_moves = [-17, -15, -10, -6, 6, 10, 15, 17]

    for move in knight_moves:
        target_square = knight_pos + move

        # Calculate file and rank of current and target squares
        current_file = knight_pos % 8
        target_file = target_square % 8

        # Check if move is within board bounds and not moving off the board edges
        if 0 <= target_square < 64 and abs(current_file - target_file) <= 2:
            moves |= 1 << target_square

    # Allow moves to enemy occupied squares
    return moves & ~(occupied & ~enemy_pieces)

occupied = (WHITE_PAWNS | BLACK_PAWNS | WHITE_KNIGHTS | BLACK_KNIGHTS |
            WHITE_BISHOPS | BLACK_BISHOPS | WHITE_ROOKS | BLACK_ROOKS |
            WHITE_QUEEN | BLACK_QUEEN | WHITE_KING | BLACK_KING)

enemy_pieces = (BLACK_PAWNS | BLACK_KNIGHTS | BLACK_BISHOPS |
                BLACK_ROOKS | BLACK_QUEEN | BLACK_KING)

print("d4 knight:")
print_bitboard(generate_knight_moves(create_bitboard('d4'), occupied, enemy_pieces))
