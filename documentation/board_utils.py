# from board import pieces, occupied
# from players import *
# from common_utils import *
# from move_generations import *



# def handle_moves(piece, color, position):
#     white_pieces = pieces.get('white_pawns', 0) | pieces.get('white_knights', 0) | pieces.get('white_bishops', 0) | pieces.get('white_rooks', 0) | pieces.get('white_queen', 0) | pieces.get('white_king', 0)
#     black_pieces = pieces.get('black_pawns', 0) | pieces.get('black_knights', 0) | pieces.get('black_bishops', 0) | pieces.get('black_rooks', 0) | pieces.get('black_queen', 0) | pieces.get('black_king', 0)

#     enemy_pieces = black_pieces if color == 'white' else white_pieces
#     position_bitboard = create_bitboard(position)

#     move_generators = {
#         'pawns': generate_pawn_moves,
#         'knights': generate_knight_moves,
#         'bishops': generate_bishop_moves,
#         'rooks': generate_rook_moves,
#         'queen': generate_queen_moves,
#         'king': generate_king_moves,
#     }

#     for key, move_generator in move_generators.items():
#         if key in piece:
#             if key == 'pawns':
#                 moves = move_generator(position_bitboard, occupied, enemy_pieces, color)
#             elif key == 'knights':
#                 moves = move_generator(position_bitboard, occupied, enemy_pieces)
#             else:
#                 moves = move_generator(from_bitboard_to_chess_position(position_bitboard), occupied, enemy_pieces)
#             break

#     return bitboard_to_square(moves)



# from app import *

# EMPTY = 0
# FULL_BOARD = 0xFFFFFFFFFFFFFFFF

# WHITE_PAWNS = 0x000000000000FF00
# WHITE_KNIGHTS = 0x0000000000000042
# WHITE_BISHOPS = 0x0000000000000024
# WHITE_ROOKS = 0x0000000000000081
# WHITE_QUEEN = 0x0000000000000008
# WHITE_KING = 0x0000000000000010

# BLACK_PAWNS = 0x00FF000000000000
# BLACK_KNIGHTS = 0x4200000000000000
# BLACK_BISHOPS = 0x2400000000000000
# BLACK_ROOKS = 0x8100000000000000
# BLACK_QUEEN = 0x0800000000000000
# BLACK_KING = 0x1000000000000000


# PIECE_SYMBOLS = {
#     'P': '♙',  # White Pawn
#     'N': '♘',  # White Knight
#     'B': '♗',  # White Bishop
#     'R': '♖',  # White Rook
#     'Q': '♕',  # White Queen
#     'K': '♔',  # White King
#     'p': '♟',  # Black Pawn
#     'n': '♞',  # Black Knight
#     'b': '♝',  # Black Bishop
#     'r': '♜',  # Black Rook
#     'q': '♛',  # Black Queen
#     'k': '♚'   # Black King
# }



# # create 1 dimensional array
# def bitboard_to_array(bitboard):
#     array = [[0 for _ in range(8)] for _ in range(8)]
#     for row in range(8):
#         for col in range(8):
#             if (bitboard >> (row * 8 + col)) & 1:
#                 array[7 - row][col] = 1
#     return array


# # print bitboard
# def print_bitboard(bitboard):
#     board = bitboard_to_array(bitboard)
#     for row in board:
#         print(" ".join(str(cell) for cell in row))


# # shift bitboard
# def shift_bitboard(bitboard, shift):
#     if shift > 0:
#         return (bitboard << shift) & FULL_BOARD
#     else:
#         return (bitboard >> -shift) & FULL_BOARD


# # create chess notation
# def chess_notation(square):
#     file = ord(square[0]) - ord('a')
#     rank = 8 - int(square[1])
#     return (rank, file)


# # create bitboard
# def create_bitboard(square):
#     file = ord(square[0]) - ord('a')
#     rank = int(square[1]) - 1
#     return 1 << (rank * 8 + file)


# # create chess notation from bitboard
# def bitboard_to_square(bitboard):
#     bit_to_square = []
#     for rank in range(8):
#         for file in range(8):
#             bit_to_square.append(chr(file + ord('a')) + str(rank + 1))
    
#     squares = []
#     for i in range(64):
#         if bitboard & (1 << i):
#             squares.append(bit_to_square[i])
    
#     return squares


# # create chess position
# def from_bitboard_to_chess_position(bitboard):
#     position = bitboard.bit_length() - 1
#     row = position // 8
#     col = position % 8
#     return (row, col)


