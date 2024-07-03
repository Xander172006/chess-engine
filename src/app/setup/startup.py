from flask import Flask, session, request
from flask_socketio import SocketIO, emit

from common_utils import *
from game.validations import validateMove


# setup game sessions
def setup_game():
    if 'game_state' not in session:
        session['turn_count'] = 0
        session['player_turn'] = 'white'
        session['game_state'] = {
            'WHITE_PAWNS': WHITE_PAWNS,
            'WHITE_KNIGHTS': WHITE_KNIGHTS,
            'WHITE_BISHOPS': WHITE_BISHOPS,
            'WHITE_ROOKS': WHITE_ROOKS,
            'WHITE_QUEEN': WHITE_QUEEN,
            'WHITE_KING': WHITE_KING,
            'BLACK_PAWNS': BLACK_PAWNS,
            'BLACK_KNIGHTS': BLACK_KNIGHTS,
            'BLACK_BISHOPS': BLACK_BISHOPS,
            'BLACK_ROOKS': BLACK_ROOKS,
            'BLACK_QUEEN': BLACK_QUEEN,
            'BLACK_KING': BLACK_KING
        }
        session['store_pieces'] = {
            'white': [],
            'black': []
        }

        session.modified = True

    # get pieces
    global bitboard_pieces
    bitboard_pieces = {
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
