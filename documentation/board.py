# from flask import session
# from players import playerTurnHandling
# from move_generations import generate_all_moves
# from common_utils import *


# def chessboard(game_state, playerTurn):
#     # players receive pieces
#     global pieces
#     pieces = playerTurnHandling(game_state, playerTurn)

#     # place pieces accordingly
#     global occupied
#     occupied = (game_state['WHITE_PAWNS'] | game_state['WHITE_KNIGHTS'] | game_state['WHITE_BISHOPS'] | game_state['WHITE_ROOKS'] | 
#                 game_state['WHITE_QUEEN'] | game_state['WHITE_KING'] | game_state['BLACK_PAWNS'] | game_state['BLACK_KNIGHTS'] | 
#                 game_state['BLACK_BISHOPS'] | game_state['BLACK_ROOKS'] | game_state['BLACK_QUEEN'] | game_state['BLACK_KING'])
    
#     # generated moves
#     global moves
#     moves = generate_all_moves(pieces, occupied, playerTurn, FULL_BOARD)
    
#     board = []

#     # create chessboard
#     for row in range(8):
#         board_row = []
#         for col in range(8):
#             color = 'white' if (row + col) % 2 == 0 else 'black'
#             board_row.append(color)
#         board.append(board_row)

#     # bitboards for all pieces
#     pieces_board = {
#             'white_pawns': bitboard_to_array(session['game_state']['WHITE_PAWNS']),
#             'white_knights': bitboard_to_array(session['game_state']['WHITE_KNIGHTS']),
#             'white_bishops': bitboard_to_array(session['game_state']['WHITE_BISHOPS']),
#             'white_rooks': bitboard_to_array(session['game_state']['WHITE_ROOKS']),
#             'white_queen': bitboard_to_array(session['game_state']['WHITE_QUEEN']),
#             'white_king': bitboard_to_array(session['game_state']['WHITE_KING']),
#             'black_pawns': bitboard_to_array(session['game_state']['BLACK_PAWNS']),
#             'black_knights': bitboard_to_array(session['game_state']['BLACK_KNIGHTS']),
#             'black_bishops': bitboard_to_array(session['game_state']['BLACK_BISHOPS']),
#             'black_rooks': bitboard_to_array(session['game_state']['BLACK_ROOKS']),
#             'black_queen': bitboard_to_array(session['game_state']['BLACK_QUEEN']),
#             'black_king': bitboard_to_array(session['game_state']['BLACK_KING']),
#     }

#     return board, pieces_board