from flask import request, jsonify, session, render_template, current_app
from devTools import devTools
from game.resources import chessResources

class chessGame:
    def __init__(self):
        from game.validations import Validation
        from setup.startup import Startup

        
        self.devTools = devTools()
        self.validation = Validation("", False, None)
        self.start = Startup()
        self.start.game_startup()
        self.playerTurn = session.get('player_turn', 'white')
        self.chessResources = chessResources(session['game_state'], session.get('player_turn', 'white'))


    # setup the game
    def runGame(self):
        self.start.game_startup()
        game_state = session['game_state']
        board, pieces_board = self.chessResources.chessboard(game_state)

        return render_template('chessboard.html', board=board, pieces=pieces_board, player_turn=self.playerTurn)
    

    # get all possible moves for a piece
    def giveMoves(self):
        data = request.get_json()
        piece_moves = self.chessResources.handle_moves(data['name'], data['color'], data['position'])

        socketio = current_app.extensions['socketio']
        socketio.emit('received-moves', {'moves': piece_moves})

        return ('', 204)
    

    def create_move(self):
        data = request.get_json()
        action = {'position': data['position'], 'placement': data['placement'], 'name': data['name'], 'color': data['color']}

        game_state = session.get('game_state')
        turn_count = session.get('turn_count', 0)
        player_turn = session.get('player_turn', 'white')

        socketio = current_app.extensions['socketio']


        # validate move
        if game_state and player_turn == action['color']:
            validation, message, captured_piece = self.validation.validateMove(action, self.chessResources.moves, game_state, self.chessResources.occupied)

            if validation:
                temp_game_state = game_state.copy()

                bitboard_pos = self.devTools.create_bitboard(action['position'])
                bitboard_dest = self.devTools.create_bitboard(action['placement'])


                temp_game_state[action['name'].upper()] ^= bitboard_pos
                temp_game_state[action['name'].upper()] |= bitboard_dest
                temp_game_state[action['name'].upper()] ^= bitboard_pos


                occupied = (temp_game_state['WHITE_PAWNS'] | temp_game_state['WHITE_KNIGHTS'] | temp_game_state['WHITE_BISHOPS'] | temp_game_state['WHITE_ROOKS'] | 
                            temp_game_state['WHITE_QUEEN'] | temp_game_state['WHITE_KING'] | temp_game_state['BLACK_PAWNS'] | temp_game_state['BLACK_KNIGHTS'] | 
                            temp_game_state['BLACK_BISHOPS'] | temp_game_state['BLACK_ROOKS'] | temp_game_state['BLACK_QUEEN'] | temp_game_state['BLACK_KING'])

                # king validation
                if self.validation.is_check(temp_game_state, occupied, player_turn):
                    socketio.emit('king-danger', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color'], 'message': "Move puts your king in check."})
                    return ('', 204)

                session['game_state'] = game_state
                session['turn_count'] = turn_count + 1
                session['player_turn'] = 'black' if player_turn == 'white' else 'white'
                session.modified = True
                
                socketio.emit('move-made', {
                        'position': action['position'],
                        'placement': action['placement'],
                        'name': action['name'],
                        'color': action['color'],
                        'captured_piece': captured_piece
                    }
                )
            else:
                # Invalid move 
                socketio.emit('invalid-move', {
                    'position': action['position'], 
                    'placement': action['placement'], 
                    'name': action['name'], 
                    'color': action['color'], 
                    'message': message
                    }
                )
        else:
            # Wrong turn
            socketio.emit('wrong-turn', {
                'position': action['position'], 
                'placement': action['placement'], 
                'name': action['name'], 
                'color': action['color']
                }
            )

        return ('', 204)
    

    def reset_board(self):
        session.clear()
        self.start.game_startup()

        prefixes = {
            'WHITE_PAWNS': 'white_pawns', 'WHITE_KNIGHTS': 'white_knights', 'WHITE_BISHOPS': 'white_bishops',
            'WHITE_ROOKS': 'white_rooks', 'WHITE_QUEEN': 'white_queen', 'WHITE_KING': 'white_king',
            'BLACK_PAWNS': 'black_pawns', 'BLACK_KNIGHTS': 'black_knights', 'BLACK_BISHOPS': 'black_bishops',
            'BLACK_ROOKS': 'black_rooks', 'BLACK_QUEEN': 'black_queen', 'BLACK_KING': 'black_king'
        }

        # return original game state
        bitboard_pieces = {prefixes[key]: self.devTools.bitboard_to_array(session['game_state'][key]) for key in prefixes}
        return jsonify(bitboard_pieces)