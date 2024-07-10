from flask import session

from app import *
from common_utils import *
from move_generations import *
from players import playerTurnHandling
import setup


# validate the move
def validateMove(action, moves, game_state, occupied):
    global WHITE_PAWNS, BLACK_PAWNS, WHITE_KNIGHTS, BLACK_KNIGHTS, WHITE_BISHOPS, BLACK_BISHOPS, WHITE_ROOKS, BLACK_ROOKS, WHITE_QUEEN, BLACK_QUEEN, WHITE_KING, BLACK_KING
    message = ""
    is_legal = False
    captured_piece = None

    global piece_mapping
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


    # player action
    bitboard_pos = create_bitboard(action['position'])
    bitboard_dest = create_bitboard(action['placement'])

    # opposition color
    enemy_color = 'black' if action['color'] == 'white' else 'white'
    enemy_pieces = 0
    my_pieces = 0

    # place enemy pieces on bitboard
    for piece, variable in piece_mapping[enemy_color].items():
        enemy_pieces |= game_state[variable]

    # place my pieces on bitboard
    for piece, variable in piece_mapping[action['color']].items():
        my_pieces |= game_state[variable]



    # pawns
    if 'pawn' in action['name']:
        color_prefix = 'white_' if action['color'] == 'white' else 'black_'
        moves[action['name'].removeprefix(color_prefix)] = generate_pawn_moves(bitboard_pos, occupied, enemy_pieces, action['color'])
        is_legal = is_legal_move(bitboard_to_array(moves['pawns']), bitboard_to_array(bitboard_dest))
    
    # knights
    if 'knight' in action['name']:
        moves['knights'] = generate_knight_moves(bitboard_pos, occupied, enemy_pieces)
        is_legal = is_legal_move(bitboard_to_array(moves['knights']), bitboard_to_array(bitboard_dest))

    # bishops
    if 'bishop' in action['name']:
        moves['bishops'] = generate_bishop_moves(from_bitboard_to_chess_position(bitboard_pos), occupied, enemy_pieces)
        is_legal = is_legal_move(bitboard_to_array(moves['bishops']), bitboard_to_array(bitboard_dest))
    
    # rooks
    if 'rook' in action['name']:
        moves['rooks'] = generate_rook_moves(from_bitboard_to_chess_position(bitboard_pos), occupied, enemy_pieces)
        is_legal = is_legal_move(bitboard_to_array(moves['rooks']), bitboard_to_array(bitboard_dest))
    
    # queen
    if 'queen' in action['name']:
        moves['queen'] = generate_queen_moves(from_bitboard_to_chess_position(bitboard_pos), occupied, enemy_pieces)
        is_legal = is_legal_move(bitboard_to_array(moves['queen']), bitboard_to_array(bitboard_dest))

    # king
    if 'king' in action['name']:
        moves['king'] = generate_king_moves(from_bitboard_to_chess_position(bitboard_pos), occupied, enemy_pieces)
        is_legal = is_legal_move(bitboard_to_array(moves['king']), bitboard_to_array(bitboard_dest))


    # check legal moves
    if is_legal:
        game_state[f"{action['name'].upper()}"] ^= bitboard_pos
        game_state[f"{action['name'].upper()}"] |= bitboard_dest

        # check for capture event
        if enemy_pieces & bitboard_dest:
            for piece, variable in piece_mapping[enemy_color].items():
                if bitboard_dest & game_state[variable]:

                    # remove captured piece
                    game_state[variable] ^= bitboard_dest
                    piecename = variable[:-1].lower()

                    # store captured pieces
                    session['store_pieces']['white'].append(piecename) if enemy_color == 'white' else session['store_pieces']['black'].append(piecename)
                    session.modified = True

                    captured_piece = piecename
                    break

    return is_legal, message, captured_piece




# compare bitboards for legal move instance
def is_legal_move(legal_moves, my_move):
    result = [[legal_moves[row][col] & my_move[row][col] for col in range(8)] for row in range(8)]
    return result == my_move



def is_check(game_state, occupied, color):
    enemy_color = 'white' if color == 'black' else 'black'
    king_pos = game_state[piece_mapping[color]['king']]

    enemy_pieces = playerTurnHandling(game_state, enemy_color)
    enemy_moves = generate_all_moves(enemy_pieces, occupied, enemy_color, full_board=None)
    my_moves = generate_all_moves(playerTurnHandling(game_state, color), occupied, color, full_board=None)

    # Check if the king's position is in the enemy's move set
    return (king_pos & enemy_moves['queen']) != 0 or \
           (king_pos & enemy_moves['rooks']) != 0 or \
           (king_pos & enemy_moves['bishops']) != 0 or \
           (king_pos & enemy_moves['knights']) != 0 or \
           (king_pos & enemy_moves['pawns']) != 0 or \
           (king_pos & enemy_moves['king']) != 0

            

def castlingRights():
    pass


def enPassant():
    pass

