from app import shift_bitboard, FULL_BOARD
from bitboard import *

from rules import is_legal_move

# moves generation
def generate_all_moves(pieces, occupied, color, full_board):
    moves = {}

    # get enemy pieces
    if color == "white":
        enemy_pieces = (pieces['black_pawns'] | pieces['black_knights'] | 
                        pieces['black_bishops'] | pieces['black_rooks'] | 
                        pieces['black_queen'] | pieces['black_king'])
    elif color == "black":
        enemy_pieces = (pieces['white_pawns'] | pieces['white_knights'] | 
                        pieces['white_bishops'] | pieces['white_rooks'] | 
                        pieces['white_queen'] | pieces['white_king']) 

    # generate moves for each piece
    moves['pawns'] = generate_pawn_moves(pieces['pawns'], occupied, enemy_pieces, color)
    moves['knights'] = generate_knight_moves(pieces['knights'], occupied, enemy_pieces)
    moves['bishops'] = generate_bishop_moves(from_bitboard_to_chess_position(pieces['bishops']), occupied, enemy_pieces)
    moves['rooks'] = generate_rook_moves(from_bitboard_to_chess_position(pieces['rooks']), occupied, enemy_pieces)
    moves['queen'] = generate_queen_moves(from_bitboard_to_chess_position(pieces['queen']), occupied, enemy_pieces)
    moves['king'] = generate_king_moves(from_bitboard_to_chess_position(pieces['king']), occupied, enemy_pieces)

    return moves



# pawn moves ✔
def generate_pawn_moves(pawns, occupied, enemy_pieces, color):
    moves = 0

    # change direction based on color
    if color == "white":
        single_step = (pawns << 8) & ~occupied
        double_step = ((single_step & 0x0000000000FF0000) << 8) & ~occupied
        capture_left = (pawns << 7) & enemy_pieces & ~0x0101010101010101
        capture_right = (pawns << 9) & enemy_pieces & ~0x8080808080808080

    elif color == "black":
        single_step = (pawns >> 8) & ~occupied
        double_step = ((single_step & 0x0000FF0000000000) >> 8) & ~occupied
        capture_left = (pawns >> 9) & enemy_pieces & ~0x0101010101010101
        capture_right = (pawns >> 7) & enemy_pieces & ~0x8080808080808080

    moves |= single_step | double_step | capture_left | capture_right
    return moves


# knight moves ✔
def generate_knight_moves(knights, occupied, enemy_pieces):
    moves = 0
    knight_pos = knights.bit_length() - 1

    knight_moves = [-17, -15, -10, -6, 6, 10, 15, 17]

    for move in knight_moves:
        target_square = knight_pos + move

        # gvie current and target file
        current_file = knight_pos % 8
        target_file = target_square % 8

        # validate move between boundaries
        if 0 <= target_square < 64 and abs(current_file - target_file) <= 2:
            moves |= 1 << target_square

    return moves & ~(occupied & ~enemy_pieces)


# bishop moves ✔
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


# queen moves ✔
def generate_queen_moves(queen, occupied, enemy_pieces):
    return generate_bishop_moves(queen, occupied, enemy_pieces) | generate_rook_moves(queen, occupied, enemy_pieces)


# king moves ✔
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


def is_king_in_check(pieces, occupied, king_pos, color):
    enemy_color = 'black' if color == 'white' else 'white'

    enemy_pieces = (pieces[f"{enemy_color}_pawns"] | pieces[f"{enemy_color}_knights"] | 
                    pieces[f"{enemy_color}_bishops"] | pieces[f"{enemy_color}_rooks"] | 
                    pieces[f"{enemy_color}_queen"] | pieces[f"{enemy_color}_king"])

    enemy_moves = generate_all_moves(pieces, occupied, enemy_color, FULL_BOARD)

    for move_set in enemy_moves.values():
        if king_pos & move_set:
            return True
        
    return False






# validate the move
def validateMove(action, moves, game_state, occupied):
    global WHITE_PAWNS, BLACK_PAWNS, WHITE_KNIGHTS, BLACK_KNIGHTS, WHITE_BISHOPS, BLACK_BISHOPS, WHITE_ROOKS, BLACK_ROOKS, WHITE_QUEEN, BLACK_QUEEN, WHITE_KING, BLACK_KING
    message = ""
    is_legal = False

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

    bitboard_pos = create_bitboard(action['position'])
    bitboard_dest = create_bitboard(action['placement'])

    enemy_color = 'black' if action['color'] == 'white' else 'white'
    enemy_pieces = 0
    my_pieces = 0

    # # place enemy pieces on bitboard
    for piece, variable in piece_mapping[enemy_color].items():
        enemy_pieces |= game_state[variable]

    for piece, variable in piece_mapping[action['color']].items():
        my_pieces |= game_state[variable]

    # debug
    print_bitboard(bitboard_pos)
    print_bitboard(enemy_pieces)
    print_bitboard(my_pieces)
    print("\n")
    print("\n")
    print("\n")

    # # check if move isnt on players own piece
    # if bitboard_pos & my_pieces:
    #     # friendly piece
    #     if bitboard_dest & my_pieces:
    #         message.append("You can't move on your own piece")
    #         return False, message
    #         # perform a bitwise and operation to check if the move is valid
    #     elif bitboard_dest & occupied:


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





    # perform move
    if is_legal:
        game_state[f"{action['name'].upper()}"] ^= bitboard_pos
        game_state[f"{action['name'].upper()}"] |= bitboard_dest

        if enemy_pieces & bitboard_dest:
            for piece, variable in piece_mapping[enemy_color].items():
                if bitboard_dest & game_state[variable]:
                    # remove enemy piece
                    game_state[variable] ^= bitboard_dest
                    piecename = variable[:-1].lower()

                    # store captured pieces
                    session['store_pieces']['white'].append(piecename) if enemy_color == 'white' else session['store_pieces']['black'].append(piecename)
                    session.modified = True
                    break





    return is_legal, message
