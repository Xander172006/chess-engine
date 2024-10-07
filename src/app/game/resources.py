from flask import session
from players import playerTurnHandling
from devTools import devTools


class chessResources:
    def __init__(self, game_state, playerTurn):
        from move_generations import MovesGeneration
        self.all_moves = MovesGeneration()
        self.devTools = devTools()

        self.pieces = {}
        self.moves = {}

        self.occupied = (game_state['WHITE_PAWNS'] | game_state['WHITE_KNIGHTS'] | game_state['WHITE_BISHOPS'] | game_state['WHITE_ROOKS'] | game_state['WHITE_QUEEN'] | game_state['WHITE_KING'] | game_state['BLACK_PAWNS'] | game_state['BLACK_KNIGHTS'] | game_state['BLACK_BISHOPS'] | game_state['BLACK_ROOKS'] | game_state['BLACK_QUEEN'] | game_state['BLACK_KING'])
        self.playerTurn = playerTurn


    def chessboard(self, game_state):
        board = []

        # create chessboard
        for row in range(8):
            board_row = []
            for col in range(8):
                color = 'white' if (row + col) % 2 == 0 else 'black'
                board_row.append(color)
            board.append(board_row)

        pieces_board = {
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

        return board, pieces_board



    # convert chess notations to handle client-side move generation
    def handle_moves(self, piece, color, position):
        white_pieces = self.pieces.get('white_pawns', 0) | self.pieces.get('white_knights', 0) | self.pieces.get('white_bishops', 0) | self.pieces.get('white_rooks', 0) | self.pieces.get('white_queen', 0) | self.pieces.get('white_king', 0)
        black_pieces = self.pieces.get('black_pawns', 0) | self.pieces.get('black_knights', 0) | self.pieces.get('black_bishops', 0) | self.pieces.get('black_rooks', 0) | self.pieces.get('black_queen', 0) | self.pieces.get('black_king', 0)

        enemy_pieces = black_pieces if color == 'white' else white_pieces
        position_bitboard = self.devTools.create_bitboard(position)

        move_generators = {
            'pawns': self.all_moves.generate_pawn_moves,
            'knights': self.all_moves.generate_knight_moves,
            'bishops': self.all_moves.generate_bishop_moves,
            'rooks': self.all_moves.generate_rook_moves,
            'queen': self.all_moves.generate_queen_moves,
            'king': self.all_moves.generate_king_moves,
        }

        # return moves
        for key, move_generator in move_generators.items():
            if key in piece:
                if key == 'pawns':
                    moves = move_generator(position_bitboard, self.occupied, enemy_pieces, color)
                elif key == 'knights':
                    moves = move_generator(position_bitboard, self.occupied, enemy_pieces)
                else:
                    moves = move_generator(self.devTools.from_bitboard_to_chess_position(position_bitboard), self.occupied, enemy_pieces)
                break

        return self.devTools.bitboard_to_square(moves)
