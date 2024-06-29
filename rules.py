from flask import session

from app import *
from moves import *
from bitboard import *







    # # check for enemy piece occupation
    # if enemy_pieces & bitboard_dest:
    #     for piece, variable in piece_mapping[enemy_color].items():
    #         if bitboard_dest & game_state[variable]:
    #             # remove enemy piece
    #             game_state[variable] ^= bitboard_dest
    #             piecename = variable[:-1].lower()

    #             # store captured pieces
    #             session['store_pieces']['white'].append(piecename) if enemy_color == 'white' else session['store_pieces']['black'].append(piecename)
    #             session.modified = True
    #             break


    # game_state[f"{action['name'].upper()}"] ^= bitboard_pos
    # game_state[f"{action['name'].upper()}"] |= bitboard_dest

    # # check valid moves
    # for piece, variable in piece_mapping[action['color']].items():
    #     if piece in action['name']:
    #         globals()[variable] = game_state[variable]
    #         break

    # return True
    
def is_legal_move(legal_moves, my_move):
    result = [[legal_moves[row][col] & my_move[row][col] for col in range(8)] for row in range(8)]
    return result == my_move
            
def castlingRights():
    pass

def enPassant():
    pass

