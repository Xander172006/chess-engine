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

def chess_notation(position):
    file = ord(position[0]) - ord('a')
    rank = int(position[1]) - 1
    return (rank, file)

def from_bitboard_to_chess_position(bitboard):
    position = bitboard.bit_length() - 1
    row = position // 8
    col = position % 8
    return (row, col)


def generate_pawn_moves(white_pawns, occupied, enemy_pieces):
    legal_moves = 0
    


    # Single move forward
    single_move = (white_pawns << 8) & ~occupied  # Move forward one square
    
    # Double move forward (only for pawns on rank 2)
    double_move = ((white_pawns & 0x0000000000FF0000) << 8) & ~occupied  # Move forward two squares
    
    # Capture moves (diagonal left and diagonal right)
    capture_left = (white_pawns << 7) & enemy_pieces & ~0x0101010101010101  # Capture diagonally left (to a5)
    capture_right = (white_pawns << 9) & enemy_pieces & ~0x8080808080808080  # Capture diagonally right
    
    # Combine all legal pawn moves
    legal_moves |= single_move | double_move | capture_left | capture_right
    
    return legal_moves










def generate_bishop_moves(bishops, occupied, enemy_pieces):
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

# rook moves ✔
def generate_rook_moves(rook, occupied, enemy_pieces):
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


def generate_queen_moves(queen, occupied, enemy_pieces):
    return generate_bishop_moves(queen, occupied, enemy_pieces) | generate_rook_moves(queen, occupied, enemy_pieces)


def generate_king_moves(king, occupied, enemy_pieces):
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




# Board and pieces definitions
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


def clear_bit(bitboard, position):
    return bitboard & ~(1 << position)


def create_bitboard(square):
    file = ord(square[0]) - ord('a')
    rank = int(square[1]) - 1
    return 1 << (rank * 8 + file)

def set_bit(bitboard, position):
    return bitboard | (1 << position)


e2_position = create_bitboard('e2').bit_length() - 1
e4_position = create_bitboard('e4').bit_length() - 1

# Set white pawn on e2 to e4
WHITE_PAWNS = clear_bit(WHITE_PAWNS, e2_position)
WHITE_PAWNS = set_bit(WHITE_PAWNS, e4_position)


# set black pawn on e7 to e5
BLACK_PAWNS = clear_bit(BLACK_PAWNS, create_bitboard('e7').bit_length() - 1)
BLACK_PAWNS = set_bit(BLACK_PAWNS, create_bitboard('e5').bit_length() - 1)


# set white pawn on f2 to f4
WHITE_PAWNS = clear_bit(WHITE_PAWNS, create_bitboard('f2').bit_length() - 1)
WHITE_PAWNS = set_bit(WHITE_PAWNS, create_bitboard('f4').bit_length() - 1)



# set black queen to h4
BLACK_QUEEN = clear_bit(BLACK_QUEEN, create_bitboard('d8').bit_length() - 1)
BLACK_QUEEN = set_bit(BLACK_QUEEN, create_bitboard('h4').bit_length() - 1)


occupied = (WHITE_PAWNS | BLACK_PAWNS | WHITE_KNIGHTS | BLACK_KNIGHTS |
            WHITE_BISHOPS | BLACK_BISHOPS | WHITE_ROOKS | BLACK_ROOKS |
            WHITE_QUEEN | BLACK_QUEEN | WHITE_KING | BLACK_KING)


enemy_pieces = (BLACK_PAWNS | BLACK_KNIGHTS | BLACK_BISHOPS |
                BLACK_ROOKS | BLACK_QUEEN | BLACK_KING)


# board state
print("Board state:")
print(print_bitboard(occupied), end="\n\n")




# generate white king moves:
king = from_bitboard_to_chess_position(WHITE_KING)
print("White king moves:")
print_bitboard(generate_king_moves(king, occupied, enemy_pieces))



