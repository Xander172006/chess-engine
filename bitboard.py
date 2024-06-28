from app import *

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


# create array
def bitboard_to_array(bitboard):
    array = [[0 for _ in range(8)] for _ in range(8)]
    for row in range(8):
        for col in range(8):
            if (bitboard >> (row * 8 + col)) & 1:
                array[7 - row][col] = 1
    return array


# display bitboard
def print_bitboard(bitboard):
    board = bitboard_to_array(bitboard)
    for row in board:
        print(" ".join(str(cell) for cell in row))


# shifts bitboard
def shift_bitboard(bitboard, shift):
    if shift > 0:
        return (bitboard << shift) & FULL_BOARD
    else:
        return (bitboard >> -shift) & FULL_BOARD


# write chess notation
def chess_notation(square):
    file = ord(square[0]) - ord('a')
    rank = 8 - int(square[1])
    return (rank, file)


# create bitboard
def create_bitboard(square):
    file = ord(square[0]) - ord('a')
    rank = int(square[1]) - 1
    return 1 << (rank * 8 + file)


def bitboard_to_square(bitboard):
    bit_to_square = []
    for rank in range(8):
        for file in range(8):
            bit_to_square.append(chr(file + ord('a')) + str(rank + 1))
    
    squares = []
    for i in range(64):
        if bitboard & (1 << i):
            squares.append(bit_to_square[i])
    
    return squares

# turn bitboard to (row, col) tuple
def from_bitboard_to_chess_position(bitboard):
    position = bitboard.bit_length() - 1
    row = position // 8
    col = position % 8
    return (row, col)
