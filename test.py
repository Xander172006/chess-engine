white_pawns = 0x000000000000FF00

def create_bitboard(square):
    file = ord(square[0]) - ord('a')
    rank = int(square[1]) - 1
    return 1 << (rank * 8 + file)

# create array
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
        double_step = ((single_step & 0x00FF000000000000) >> 8) & ~occupied

        # captures
        capture_left = (pawns >> 9) & enemy_pieces & ~0x0101010101010101
        capture_right = (pawns >> 7) & enemy_pieces & ~0x8080808080808080
        
    moves |= single_step | double_step | capture_left | capture_right
    return moves


# return the moves for the one pawn on e2
print_bitboard(generate_pawn_moves(create_bitboard('g2'), 0, 0, 'white'))