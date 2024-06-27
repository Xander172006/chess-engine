EMPTY = 0
FULL_BOARD = 0xFFFFFFFFFFFFFFFF

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

def shift_bitboard(bitboard, shift):
    if shift > 0:
        return (bitboard << shift) & FULL_BOARD
    else:
        return (bitboard >> -shift) & FULL_BOARD

def print_bitboard(bitboard):
    board = bitboard_to_array(bitboard)
    for row in board:
        print(" ".join(str(cell) for cell in row))

def generate_bishop_moves(bishops, occupied, enemy_pieces):
    bishop_moves = 0
    directions = [-9, -7, 7, 9]
    for shift in directions:
        ray = shift_bitboard(bishops, shift)
        while ray:
            bishop_moves |= ray
            # Check for edge boundaries
            if shift in [-9, 7]:  # leftward shifts
                if ray & 0x0101010101010101:  # pieces in column 'a'
                    break
            if shift in [-7, 9]:  # rightward shifts
                if ray & 0x8080808080808080:  # pieces in column 'h'
                    break
            ray &= ~occupied
            ray = shift_bitboard(ray, shift)
    return bishop_moves & ~(occupied & ~enemy_pieces)


occupied = (WHITE_PAWNS | BLACK_PAWNS | WHITE_KNIGHTS | BLACK_KNIGHTS |
            WHITE_BISHOPS | BLACK_BISHOPS | WHITE_ROOKS | BLACK_ROOKS |
            WHITE_QUEEN | BLACK_QUEEN | WHITE_KING | BLACK_KING)

enemy_pieces = (BLACK_PAWNS | BLACK_KNIGHTS | BLACK_BISHOPS |
                BLACK_ROOKS | BLACK_QUEEN | BLACK_KING)

print("f1 knight:")
print_bitboard(generate_bishop_moves(create_bitboard('f1'), occupied, enemy_pieces))
