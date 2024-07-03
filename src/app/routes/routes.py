from flask import Blueprint, request, jsonify, session, render_template, current_app
from game.logic import chessboard, handle_moves
from flask_socketio import SocketIO, emit

bp = Blueprint('main', __name__)


# main page
@bp.route('/')
def public():
    from setup.startup import setup_game

    setup_game()
    game_state = session['game_state']
    player_turn = session.get('player_turn', 'white')
    board, pieces_board = chessboard(game_state, player_turn)

    return render_template('chessboard.html', board=board, pieces=pieces_board, player_turn=player_turn)



# return moves to client
@bp.route('/get-moves', methods=['POST'])
def get_moves():
    data = request.get_json()
    piece_moves = handle_moves(data['name'], data['color'], data['position'])

    socketio = current_app.extensions['socketio']
    socketio.emit('received-moves', {'moves': piece_moves})

    return ('', 204)



# create move from client
@bp.route('/make_move', methods=['POST'])
def create_move():
    from flask_socketio import SocketIO 
    from game.validations import validateMove
    from game.logic import moves, occupied

    data = request.get_json()
    action = {'position': data['position'], 'placement': data['placement'], 'name': data['name'], 'color': data['color']}

    game_state = session.get('game_state')
    turn_count = session.get('turn_count', 0)
    player_turn = session.get('player_turn', 'white')

    socketio = current_app.extensions['socketio']

    # validate move
    if game_state and player_turn == action['color']:
        validation, message = validateMove(action, moves, game_state, occupied)
        if validation:
            session['game_state'] = game_state
            session['turn_count'] = turn_count + 1
            session['player_turn'] = 'black' if player_turn == 'white' else 'white'
            session.modified = True
            
            # valid move
            socketio.emit('move-made', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color']})
        else:
            # invalid move
            socketio.emit('invalid-move', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color'], 'message': message})
    else:
        # wrong turn
        socketio.emit('wrong-turn', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color']})

    return ('', 204)



# reset game sessions
@bp.route('/reset_board', methods=['POST'])
def reset_board():
    from flask_socketio import SocketIO
    from setup.startup import setup_game
    from common_utils import bitboard_to_array

    session.clear()
    setup_game()

    prefixes = {
        'WHITE_PAWNS': 'white_pawns', 'WHITE_KNIGHTS': 'white_knights', 'WHITE_BISHOPS': 'white_bishops',
        'WHITE_ROOKS': 'white_rooks', 'WHITE_QUEEN': 'white_queen', 'WHITE_KING': 'white_king',
        'BLACK_PAWNS': 'black_pawns', 'BLACK_KNIGHTS': 'black_knights', 'BLACK_BISHOPS': 'black_bishops',
        'BLACK_ROOKS': 'black_rooks', 'BLACK_QUEEN': 'black_queen', 'BLACK_KING': 'black_king'
    }

    # return original game state
    bitboard_pieces = {prefixes[key]: bitboard_to_array(session['game_state'][key]) for key in prefixes}
    return jsonify(bitboard_pieces)