from flask import session

from app import *
from devTools import devTools
from move_generations import MovesGeneration
from players import playerTurnHandling


# create the same code structure but with object-oriented programming
class Validation:
    def __init__(self, message, is_legal, captured_piece):
        global WHITE_PAWNS, BLACK_PAWNS, WHITE_KNIGHTS, BLACK_KNIGHTS, WHITE_BISHOPS, BLACK_BISHOPS, WHITE_ROOKS, BLACK_ROOKS, WHITE_QUEEN, BLACK_QUEEN, WHITE_KING, BLACK_KING
        global piece_mapping

        self.devTools = devTools()
        self.all_moves = MovesGeneration()
        
        self.message = message
        self.is_legal = is_legal
        self.king_has_moved = False
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

    # validate the move
    def validateMove(self, action, moves, game_state, occupied):
        # player action
        bitboard_pos = self.devTools.create_bitboard(action['position'])
        bitboard_dest = self.devTools.create_bitboard(action['placement'])

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


        temp_game_state = game_state.copy()


        # pawns
        if 'pawn' in action['name']:
            color_prefix = 'white_' if action['color'] == 'white' else 'black_'
            moves[action['name'].removeprefix(color_prefix)] = self.all_moves.generate_pawn_moves(bitboard_pos, occupied, enemy_pieces, action['color'])
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
            if not self.is_check(temp_game_state, occupied, action['color']):
                if self.king_has_moved == False:
                    self.castlingRights(action, game_state, moves, occupied, bitboard_dest)
                    
                
        


        # check legal moves
        if self.is_legal:
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
        my_moves = MovesGeneration().generate_all_moves(playerTurnHandling(game_state, color), occupied, color)

        # Check if the king's position is in the enemy's move set
        return (king_pos & enemy_moves['queen']) != 0 or \
            (king_pos & enemy_moves['rooks']) != 0 or \
            (king_pos & enemy_moves['bishops']) != 0 or \
            (king_pos & enemy_moves['knights']) != 0 or \
            (king_pos & enemy_moves['pawns']) != 0 or \
            (king_pos & enemy_moves['king']) != 0


    def castlingRights(self, action, game_state, moves, occupied, bitboard_dest):
        if action['name'] == 'white_king':
            if action['position'] == 'e1' and action['placement'] == 'g1':
                if game_state['WHITE_ROOKS'] & self.devTools.create_bitboard('h1') and not game_state['WHITE_KING'] & self.devTools.create_bitboard('f1'):
                    game_state['WHITE_ROOKS'] ^= self.devTools.create_bitboard('h1')
                    game_state['WHITE_ROOKS'] |= self.devTools.create_bitboard('f1')
                    self.is_legal = True
                else:
                    self.is_legal = False

            elif action['position'] == 'e1' and action['placement'] == 'c1':
                if game_state['WHITE_ROOKS'] & self.devTools.create_bitboard('a1') and not game_state['WHITE_KING'] & self.devTools.create_bitboard('d1'):
                    game_state['WHITE_ROOKS'] ^= self.devTools.create_bitboard('a1')
                    game_state['WHITE_ROOKS'] |= self.devTools.create_bitboard('d1')
                    self.is_legal = True
                else:
                    self.is_legal = False
            else:
                self.is_legal = self.is_legal_move(self.devTools.bitboard_to_array(moves['king']), self.devTools.bitboard_to_array(bitboard_dest))

        elif action['name'] == 'black_king': 
            if action['position'] == 'e8' and action['placement'] == 'g8':
                if game_state['BLACK_ROOKS'] & self.devTools.create_bitboard('h8') and not game_state['BLACK_KING'] & self.devTools.create_bitboard('f8'):
                    game_state['BLACK_ROOKS'] ^= self.devTools.create_bitboard('h8')
                    game_state['BLACK_ROOKS'] |= self.devTools.create_bitboard('f8')
                    self.is_legal = True
                else:
                    self.is_legal = False
                    
            elif action['position'] == 'e8' and action['placement'] == 'c8':
                if game_state['BLACK_ROOKS'] & self.devTools.create_bitboard('a8') and not game_state['BLACK_KING'] & self.devTools.create_bitboard('d8'):
                    game_state['BLACK_ROOKS'] ^= self.devTools.create_bitboard('a8')
                    game_state['BLACK_ROOKS'] |= self.devTools.create_bitboard('d8')
                    self.is_legal = True
                else:
                    self.is_legal = False
            else:
                self.is_legal = self.is_legal_move(self.devTools.bitboard_to_array(moves['king']), self.devTools.bitboard_to_array(bitboard_dest))


    def enPassant():
        pass



laat x gelijk aan (true) ? 1 : 2; 

        