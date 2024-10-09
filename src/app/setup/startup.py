from flask import session
from devTools import devTools

class Startup:
    def __init__ (self):
        self.devTools = devTools()


    # setup game sessions
    def game_startup(self):
        if 'game_state' not in session:
            session['turn_count'] = 0
            session['player_turn'] = 'white'
            session['game_state'] = {
                'WHITE_PAWNS': devTools().WHITE_PAWNS,
                'WHITE_KNIGHTS': devTools().WHITE_KNIGHTS,
                'WHITE_BISHOPS': devTools().WHITE_BISHOPS,
                'WHITE_ROOKS': devTools().WHITE_ROOKS,
                'WHITE_QUEEN': devTools().WHITE_QUEEN,
                'WHITE_KING': devTools().WHITE_KING,
                'BLACK_PAWNS': devTools().BLACK_PAWNS,
                'BLACK_KNIGHTS': devTools().BLACK_KNIGHTS,
                'BLACK_BISHOPS': devTools().BLACK_BISHOPS,
                'BLACK_ROOKS': devTools().BLACK_ROOKS,
                'BLACK_QUEEN': devTools().BLACK_QUEEN,
                'BLACK_KING': devTools().BLACK_KING,

                'white_king_has_moved': False,
                'black_king_has_moved': False
            }
            session['store_pieces'] = {'white': [], 'black': []}

            session['pawn-moved-2-steps'] = None
            session.modified = True

        # get pieces
        global bitboard_pieces
        bitboard_pieces = {
                'white_pawns': self.devTools.bitboard_to_array(session['game_state']['WHITE_PAWNS']),
                'white_knights': self.devTools.bitboard_to_array(session['game_state']['WHITE_KNIGHTS']),
                'white_bishops': self.devTools.bitboard_to_array(session['game_state']['WHITE_BISHOPS']),
                'white_rooks': self.devTools.bitboard_to_array(session['game_state']['WHITE_ROOKS']),
                'white_queen': self.devTools.bitboard_to_array(session['game_state']['WHITE_QUEEN']),
                'white_king': self.devTools.bitboard_to_array(session['game_state']['WHITE_KING']),
                'black_pawns': self.devTools.bitboard_to_array(session['game_state']['BLACK_PAWNS']),
                'black_knights': self.devTools.bitboard_to_array(session['game_state']['BLACK_KNIGHTS']),
                'black_bishops': self.devTools.bitboard_to_array(session['game_state']['BLACK_BISHOPS']),
                'black_rooks': self.devTools.bitboard_to_array(session['game_state']['BLACK_ROOKS']),
                'black_queen': self.devTools.bitboard_to_array(session['game_state']['BLACK_QUEEN']),
                'black_king': self.devTools.bitboard_to_array(session['game_state']['BLACK_KING']),
        }
