from flask import session

from app import *
from moves import *
from bitboard import *


# validate the move
def validateMove(action, moves, game_state, turn_count):
    global WHITE_PAWNS, BLACK_PAWNS, WHITE_KNIGHTS, BLACK_KNIGHTS, WHITE_BISHOPS, BLACK_BISHOPS, WHITE_ROOKS, BLACK_ROOKS, WHITE_QUEEN, BLACK_QUEEN, WHITE_KING, BLACK_KING
    result = []

    piece_mapping = {
        'white': {
            'pawn': 'WHITE_PAWNS',
            'knight': 'WHITE_KNIGHTS',
            'bishop': 'WHITE_BISHOPS',
            'rook': 'WHITE_ROOKS',
            'queen': 'WHITE_QUEEN',
            'king': 'WHITE_KING'
        },
        'black': {
            'pawn': 'BLACK_PAWNS',
            'knight': 'BLACK_KNIGHTS',
            'bishop': 'BLACK_BISHOPS',
            'rook': 'BLACK_ROOKS',
            'queen': 'BLACK_QUEEN',
            'king': 'BLACK_KING'
        }
    }

    # create bitboards
    bitboard_pos = create_bitboard(action['position'])
    bitboard_dest = create_bitboard(action['placement'])

    # given the position, find the piece
    enemy_color = 'black' if action['color'] == 'white' else 'white'
    enemy_pieces = 0
    for piece, variable in piece_mapping[enemy_color].items():
        enemy_pieces |= game_state[variable]

    # capture the enemy piece
    if enemy_pieces & bitboard_dest:
        for piece, variable in piece_mapping[enemy_color].items():
            if bitboard_dest & game_state[variable]:
                game_state[variable] ^= bitboard_dest
                piecename = variable[:-1].lower()

                session['store_pieces']['white'].append(piecename) if enemy_color == 'white' else session['store_pieces']['black'].append(piecename)
                session.modified = True
                break


    game_state[f"{action['name'].upper()}"] ^= bitboard_pos
    game_state[f"{action['name'].upper()}"] |= bitboard_dest

    for piece, variable in piece_mapping[action['color']].items():
        if piece in action['name']:
            globals()[variable] = game_state[variable]
            break

    return True

    
            
def castlingRights():
    pass

def enPassant():
    pass
