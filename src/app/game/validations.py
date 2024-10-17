from flask import session

from app import *
from devTools import devTools
from move_generations import MovesGeneration
from players import playerTurnHandling


# create the same code structure but with object-oriented programming
class Validation:
    king_has_moved = False

    def __init__(self, message, is_legal, captured_piece):
        global WHITE_PAWNS, BLACK_PAWNS, WHITE_KNIGHTS, BLACK_KNIGHTS, WHITE_BISHOPS, BLACK_BISHOPS, WHITE_ROOKS, BLACK_ROOKS, WHITE_QUEEN, BLACK_QUEEN, WHITE_KING, BLACK_KING
        global piece_mapping

        self.devTools = devTools()
        self.all_moves = MovesGeneration()
        
        self.message = message
        self.is_legal = is_legal
        self.captured_piece = captured_piece
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

    
    def validateMove(self, action, moves, game_state, occupied):
        bitboard_pos = self.devTools.create_bitboard(action['position'])
        bitboard_dest = self.devTools.create_bitboard(action['placement'])

        # opposition color
        enemy_color = 'black' if action['color'] == 'white' else 'white'
        enemy_pieces = 0
        my_pieces = 0

        # place enemy pieces
        for piece, variable in piece_mapping[enemy_color].items():
            enemy_pieces |= game_state[variable]

        # place my pieces
        for piece, variable in piece_mapping[action['color']].items():
            my_pieces |= game_state[variable]


        # pawns
        if 'pawn' in action['name']:
            color_prefix = 'white_' if action['color'] == 'white' else 'black_'
            moves[action['name'].removeprefix(color_prefix)] = self.all_moves.generate_pawn_moves(bitboard_pos, occupied, enemy_pieces, action['color'])



            if self.all_moves.pawn_moved_2_steps & bitboard_dest:
                session['pawn-moved-2-steps'] = action['placement']  # Store the destination square for en passant check
                session.modified = True

            if self.enPassant(action['position'], action['color'], game_state):
                self.is_legal = True
            else:
                self.is_legal = self.is_legal_move(self.devTools.bitboard_to_array(moves['pawns']), self.devTools.bitboard_to_array(bitboard_dest))
        
        # knights
        if 'knight' in action['name']:
            moves['knights'] = self.all_moves.generate_knight_moves(bitboard_pos, occupied, enemy_pieces)
            self.is_legal = self.is_legal_move(self.devTools.bitboard_to_array(moves['knights']), self.devTools.bitboard_to_array(bitboard_dest))

        # bishops
        if 'bishop' in action['name']:
            moves['bishops'] = self.all_moves.generate_bishop_moves(self.devTools.from_bitboard_to_chess_position(bitboard_pos), occupied, enemy_pieces)
            self.is_legal = self.is_legal_move(self.devTools.bitboard_to_array(moves['bishops']), self.devTools.bitboard_to_array(bitboard_dest))

        # rooks
        if 'rook' in action['name']:
            moves['rooks'] = self.all_moves.generate_rook_moves(self.devTools.from_bitboard_to_chess_position(bitboard_pos), occupied, enemy_pieces)
            self.is_legal = self.is_legal_move(self.devTools.bitboard_to_array(moves['rooks']), self.devTools.bitboard_to_array(bitboard_dest))

        # queen
        if 'queen' in action['name']:
            moves['queen'] = self.all_moves.generate_queen_moves(self.devTools.from_bitboard_to_chess_position(bitboard_pos), occupied, enemy_pieces)
            self.is_legal = self.is_legal_move(self.devTools.bitboard_to_array(moves['queen']), self.devTools.bitboard_to_array(bitboard_dest))

        # king
        if 'king' in action['name']:
            moves['king'] = self.all_moves.generate_king_moves(self.devTools.from_bitboard_to_chess_position(bitboard_pos), occupied, enemy_pieces)
            if not self.is_check(game_state, occupied, action['color']):
                self.castlingRights(action, game_state, moves, occupied, bitboard_dest)

                
        


        # check legal moves
        if self.is_legal:
            game_state[f"{action['name'].upper()}"] ^= bitboard_pos
            game_state[f"{action['name'].upper()}"] |= bitboard_dest
            # print(f"game_state variable: {self.devTools.print_bitboard(game_state[action['name'].upper()])}")
            # check for capture event
            if enemy_pieces & bitboard_dest:
                for piece, variable in piece_mapping[enemy_color].items():
                    # print(f"bitboard_dest: {self.devTools.print_bitboard(bitboard_dest)}")
                    # print(f"game_state variable: {self.devTools.print_bitboard(game_state[variable])}")
                    if bitboard_dest & game_state[variable]:

                        # remove captured piece
                        game_state[variable] ^= bitboard_dest
                        piecename = variable[:-1].lower()

                        # store captured pieces
                        session['store_pieces']['white'].append(piecename) if enemy_color == 'white' else session['store_pieces']['black'].append(piecename)
                        session.modified = True

                        self.captured_piece = piecename
                        break

        return self.is_legal, self.message, self.captured_piece
    
    def is_legal_move(self, legal_moves, my_move):
        result = [[legal_moves[row][col] & my_move[row][col] for col in range(8)] for row in range(8)]
        return result == my_move
    

    def is_check(self, game_state, occupied, color):
        enemy_color = 'white' if color == 'black' else 'black'
        king_pos = game_state[piece_mapping[color]['king']]

        enemy_pieces = playerTurnHandling(game_state, enemy_color)
        enemy_moves = MovesGeneration().generate_all_moves(enemy_pieces, occupied, enemy_color)

        # Check if the king's position is in the enemy's move set
        return (king_pos & enemy_moves['queen']) != 0 or \
            (king_pos & enemy_moves['rooks']) != 0 or \
            (king_pos & enemy_moves['bishops']) != 0 or \
            (king_pos & enemy_moves['knights']) != 0 or \
            (king_pos & enemy_moves['pawns']) != 0 or \
            (king_pos & enemy_moves['king']) != 0


    def castlingRights(self, action, game_state, moves, occupied, bitboard_dest):
        king_positions = {
            'white_king': ('e1', 'white_king_has_moved', 'WHITE_ROOKS', 'WHITE_KING'),
            'black_king': ('e8', 'black_king_has_moved', 'BLACK_ROOKS', 'BLACK_KING')
        }
        
        if action['name'] in king_positions:
            king_pos, king_moved, rooks, king = king_positions[action['name']]
            
            if action['position'] == king_pos and not game_state[king_moved]:
                if action['placement'] == 'g' + king_pos[1]:
                    # Check that f1 and g1 (or f8 and g8 for black) are empty for kingside castling
                    if game_state[rooks] & self.devTools.create_bitboard('h' + king_pos[1]) and \
                    not game_state[king] & self.devTools.create_bitboard('f' + king_pos[1]) and \
                    not occupied & self.devTools.create_bitboard('f' + king_pos[1]) and \
                    not occupied & self.devTools.create_bitboard('g' + king_pos[1]):
                        game_state[rooks] ^= self.devTools.create_bitboard('h' + king_pos[1])
                        game_state[rooks] |= self.devTools.create_bitboard('f' + king_pos[1])
                        game_state[king_moved] = True
                        self.is_legal = True
                
                elif action['placement'] == 'c' + king_pos[1]:
                    # Check that b1, c1, and d1 (or b8, c8, d8 for black) are empty for queenside castling
                    if game_state[rooks] & self.devTools.create_bitboard('a' + king_pos[1]) and \
                    not game_state[king] & self.devTools.create_bitboard('d' + king_pos[1]) and \
                    not occupied & self.devTools.create_bitboard('b' + king_pos[1]) and \
                    not occupied & self.devTools.create_bitboard('c' + king_pos[1]) and \
                    not occupied & self.devTools.create_bitboard('d' + king_pos[1]):
                        game_state[rooks] ^= self.devTools.create_bitboard('a' + king_pos[1])
                        game_state[rooks] |= self.devTools.create_bitboard('d' + king_pos[1])
                        game_state[king_moved] = True
                        self.is_legal = True
                else:
                    self.is_legal = self.is_legal_move(self.devTools.bitboard_to_array(moves['king']), self.devTools.bitboard_to_array(bitboard_dest))
                    game_state[king_moved] = True
            else:
                self.is_legal = self.is_legal_move(self.devTools.bitboard_to_array(moves['king']), self.devTools.bitboard_to_array(bitboard_dest))
                game_state[king_moved] = True




    def enPassant(self, move, color, game_state):
        last_pawn_move = session.get('pawn-moved-2-steps')

        if last_pawn_move:
            # Determine which rank the captured pawn is on
            captured_pawn_rank = '5' if color == 'white' else '4'
            destination_rank = '6' if color == 'white' else '3'


            if move[1] == last_pawn_move[1] and abs(ord(move[0]) - ord(last_pawn_move[0])) == 1:
                # Position of the captured pawn
                captured_pawn_pos = last_pawn_move[0] + captured_pawn_rank
                captured_pawn_bitboard = self.devTools.create_bitboard(captured_pawn_pos)


                # Remove the captured pawn from the game state
                if color == 'white':
                    game_state['BLACK_PAWNS'] &= ~captured_pawn_bitboard 
                    piecename = 'pawn'
                    session['store_pieces']['white'].append(piecename)  # Store captured piece
                else:
                    game_state['WHITE_PAWNS'] &= ~captured_pawn_bitboard 
                    piecename = 'pawn'
                    session['store_pieces']['black'].append(piecename)  # Store captured piece

                session.modified = True
                return True
            else:
                return False

        return False


    def can_promote():
        pass



        