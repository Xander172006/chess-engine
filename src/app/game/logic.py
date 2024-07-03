from flask import session
from players import playerTurnHandling
from move_generations import *


# chessboard function with utils
def chessboard(game_state, playerTurn):
    # get pieces
    global pieces
    pieces = playerTurnHandling(game_state, playerTurn)

    # get piece placement
    global occupied
    occupied = (game_state['WHITE_PAWNS'] | game_state['WHITE_KNIGHTS'] | game_state['WHITE_BISHOPS'] | game_state['WHITE_ROOKS'] | 
                game_state['WHITE_QUEEN'] | game_state['WHITE_KING'] | game_state['BLACK_PAWNS'] | game_state['BLACK_KNIGHTS'] | 
                game_state['BLACK_BISHOPS'] | game_state['BLACK_ROOKS'] | game_state['BLACK_QUEEN'] | game_state['BLACK_KING'])
    
    # generate moves
    global moves
    moves = generate_all_moves(pieces, occupied, playerTurn, FULL_BOARD)
    
    board = []

    # create chessboard
    for row in range(8):
        board_row = []
        for col in range(8):
            color = 'white' if (row + col) % 2 == 0 else 'black'
            board_row.append(color)
        board.append(board_row)

    pieces_board = {
            'white_pawns': bitboard_to_array(session['game_state']['WHITE_PAWNS']),
            'white_knights': bitboard_to_array(session['game_state']['WHITE_KNIGHTS']),
            'white_bishops': bitboard_to_array(session['game_state']['WHITE_BISHOPS']),
            'white_rooks': bitboard_to_array(session['game_state']['WHITE_ROOKS']),
            'white_queen': bitboard_to_array(session['game_state']['WHITE_QUEEN']),
            'white_king': bitboard_to_array(session['game_state']['WHITE_KING']),
            'black_pawns': bitboard_to_array(session['game_state']['BLACK_PAWNS']),
            'black_knights': bitboard_to_array(session['game_state']['BLACK_KNIGHTS']),
            'black_bishops': bitboard_to_array(session['game_state']['BLACK_BISHOPS']),
            'black_rooks': bitboard_to_array(session['game_state']['BLACK_ROOKS']),
            'black_queen': bitboard_to_array(session['game_state']['BLACK_QUEEN']),
            'black_king': bitboard_to_array(session['game_state']['BLACK_KING']),
    }

    return board, pieces_board



# convert chess notations to handle client-side move generation
def handle_moves(piece, color, position):
    white_pieces = pieces.get('white_pawns', 0) | pieces.get('white_knights', 0) | pieces.get('white_bishops', 0) | pieces.get('white_rooks', 0) | pieces.get('white_queen', 0) | pieces.get('white_king', 0)
    black_pieces = pieces.get('black_pawns', 0) | pieces.get('black_knights', 0) | pieces.get('black_bishops', 0) | pieces.get('black_rooks', 0) | pieces.get('black_queen', 0) | pieces.get('black_king', 0)

    enemy_pieces = black_pieces if color == 'white' else white_pieces
    position_bitboard = create_bitboard(position)

    move_generators = {
        'pawns': generate_pawn_moves,
        'knights': generate_knight_moves,
        'bishops': generate_bishop_moves,
        'rooks': generate_rook_moves,
        'queen': generate_queen_moves,
        'king': generate_king_moves,
    }

    # return moves
    for key, move_generator in move_generators.items():
        if key in piece:
            if key == 'pawns':
                moves = move_generator(position_bitboard, occupied, enemy_pieces, color)
            elif key == 'knights':
                moves = move_generator(position_bitboard, occupied, enemy_pieces)
            else:
                moves = move_generator(from_bitboard_to_chess_position(position_bitboard), occupied, enemy_pieces)
            break

    return bitboard_to_square(moves)
