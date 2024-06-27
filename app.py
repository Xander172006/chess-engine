from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit

from moves import *
from bitboard import *
from rules import validateMove


# create app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# connect
@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


def initialize_game_state():
    if 'game_state' not in session:
        session['game_state'] = {
            'WHITE_PAWNS': 0x000000000000FF00,
            'WHITE_KNIGHTS': 0x0000000000000042,
            'WHITE_BISHOPS': 0x0000000000000024,
            'WHITE_ROOKS': 0x0000000000000081,
            'WHITE_QUEEN': 0x0000000000000008,
            'WHITE_KING': 0x0000000000000010,
            'BLACK_PAWNS': 0x00FF000000000000,
            'BLACK_KNIGHTS': 0x4200000000000000,
            'BLACK_BISHOPS': 0x2400000000000000,
            'BLACK_ROOKS': 0x8100000000000000,
            'BLACK_QUEEN': 0x0800000000000000,
            'BLACK_KING': 0x1000000000000000,
        }
        session['turn_count'] = 0
        session['player_turn'] = 'white'
        session['store_pieces'] = {
            'white': [],
            'black': []
        }
        session.modified = True



# handle move event
@app.route('/make-move', methods=['POST'])
def create_move():
    if request.method == 'POST':
        data = request.get_json()
        action = {
            'position': data['position'],
            'placement': data['placement'],
            'name': data['name'],
            'color': data['color']
        }

        game_state = session.get('game_state')
        turn_count = session.get('turn_count', 0)
        player_turn = session.get('player_turn', 'white')

        if game_state and player_turn == action['color']:
            validation = validateMove(action, moves, game_state, turn_count)
            if validation:
                session['game_state'] = game_state
                session['turn_count'] = turn_count + 1
                session['player_turn'] = 'black' if player_turn == 'white' else 'white'
                session.modified = True
                socketio.emit('move-made', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color']})
            else:
                # invalid move
                socketio.emit('invalid-move', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color']})
        else:
            # wrong players turn
            socketio.emit('wrong-turn', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color']})




    return ('', 204)


# reset board
@app.route('/reset-board', methods=['POST'])
def reset_board():
    session.pop('game_state', None)
    session.pop('player_turn', None)
    session.pop('store_pieces', None)
    initialize_game_state()
    game_state = session['game_state']

    pieces_board = {
        'white_pawns': bitboard_to_array(game_state['WHITE_PAWNS']),
        'black_pawns': bitboard_to_array(game_state['BLACK_PAWNS']),
        'white_rooks': bitboard_to_array(game_state['WHITE_ROOKS']),
        'black_rooks': bitboard_to_array(game_state['BLACK_ROOKS']),
        'white_knights': bitboard_to_array(game_state['WHITE_KNIGHTS']),
        'black_knights': bitboard_to_array(game_state['BLACK_KNIGHTS']),
        'white_bishops': bitboard_to_array(game_state['WHITE_BISHOPS']),
        'black_bishops': bitboard_to_array(game_state['BLACK_BISHOPS']),
        'white_queen': bitboard_to_array(game_state['WHITE_QUEEN']),
        'black_queen': bitboard_to_array(game_state['BLACK_QUEEN']),
        'white_king': bitboard_to_array(game_state['WHITE_KING']),
        'black_king': bitboard_to_array(game_state['BLACK_KING']),
    }

    return jsonify(pieces_board)



# chessboard operator
def chessboard(game_state, playerTurn):
    global pieces
    pieces = playerTurnHandling(game_state, playerTurn)

    # occupied squares
    global occupied
    occupied = (game_state['WHITE_PAWNS'] | game_state['WHITE_KNIGHTS'] | game_state['WHITE_BISHOPS'] | game_state['WHITE_ROOKS'] | 
                game_state['WHITE_QUEEN'] | game_state['WHITE_KING'] | game_state['BLACK_PAWNS'] | game_state['BLACK_KNIGHTS'] | 
                game_state['BLACK_BISHOPS'] | game_state['BLACK_ROOKS'] | game_state['BLACK_QUEEN'] | game_state['BLACK_KING'])
    
    # generate all moves
    global moves
    moves = generate_all_moves(pieces, occupied, playerTurn, FULL_BOARD)
    board = []



    # create chessboard
    for row in range(8):
        board_row = []
        for col in range(8):
            color = 'white' if (row + col) % 2 == 0 else 'black'
            board_row.append(color)
        board.append(board_row)

    # bitboards for all pieces
    pieces_board = {
        'white_pawns': bitboard_to_array(game_state['WHITE_PAWNS']),
        'black_pawns': bitboard_to_array(game_state['BLACK_PAWNS']),
        'white_rooks': bitboard_to_array(game_state['WHITE_ROOKS']),
        'black_rooks': bitboard_to_array(game_state['BLACK_ROOKS']),
        'white_knights': bitboard_to_array(game_state['WHITE_KNIGHTS']),
        'black_knights': bitboard_to_array(game_state['BLACK_KNIGHTS']),
        'white_bishops': bitboard_to_array(game_state['WHITE_BISHOPS']),
        'black_bishops': bitboard_to_array(game_state['BLACK_BISHOPS']),
        'white_queen': bitboard_to_array(game_state['WHITE_QUEEN']),
        'black_queen': bitboard_to_array(game_state['BLACK_QUEEN']),
        'white_king': bitboard_to_array(game_state['WHITE_KING']),
        'black_king': bitboard_to_array(game_state['BLACK_KING']),
    }

    return board, pieces_board


# turn handling
def playerTurnHandling(game_state, color):
    if color == 'white':
        pieces = {
            'pawns': game_state['WHITE_PAWNS'],
            'knights': game_state['WHITE_KNIGHTS'],
            'bishops': game_state['WHITE_BISHOPS'],
            'rooks': game_state['WHITE_ROOKS'],
            'queen': game_state['WHITE_QUEEN'],
            'king': game_state['WHITE_KING'],
            'black_pawns': game_state['BLACK_PAWNS'],
            'black_knights': game_state['BLACK_KNIGHTS'],
            'black_bishops': game_state['BLACK_BISHOPS'],
            'black_rooks': game_state['BLACK_ROOKS'],
            'black_queen': game_state['BLACK_QUEEN'],
            'black_king': game_state['BLACK_KING'],
        }
    elif color == 'black':
        pieces = {
            'pawns': game_state['BLACK_PAWNS'],
            'knights': game_state['BLACK_KNIGHTS'],
            'bishops': game_state['BLACK_BISHOPS'],
            'rooks': game_state['BLACK_ROOKS'],
            'queen': game_state['BLACK_QUEEN'],
            'king': game_state['BLACK_KING'],
            'white_pawns': game_state['WHITE_PAWNS'],
            'white_knights': game_state['WHITE_KNIGHTS'],
            'white_bishops': game_state['WHITE_BISHOPS'],
            'white_rooks': game_state['WHITE_ROOKS'],
            'white_queen': game_state['WHITE_QUEEN'],
            'white_king': game_state['WHITE_KING'],
    }

    return pieces


# run the engine
@app.route('/')
def runEngine():
    initialize_game_state()
    game_state = session['game_state']

    playerTurn = session.get('player_turn', 'white')
    board, pieces_board = chessboard(game_state, playerTurn)
    
    return render_template('chessboard.html', board=board, pieces=pieces_board, playerTurn=playerTurn)


@app.route('/get-moves', methods=['POST'])
def get_moves():
    data = request.get_json()
    print(data)

    if 'pawns' in data['name']:
        if data['color'] == 'white':
            enemy_pieces = pieces.get('black_pawns', 0) | pieces.get('black_knights', 0) | pieces.get('black_bishops', 0) | pieces.get('black_rooks', 0) | pieces.get('black_queen', 0) | pieces.get('black_king', 0)
        else:
            enemy_pieces = pieces.get('white_pawns', 0) | pieces.get('white_knights', 0) | pieces.get('white_bishops', 0) | pieces.get('white_rooks', 0) | pieces.get('white_queen', 0) | pieces.get('white_king', 0)
            
        moves = generate_pawn_moves(create_bitboard(data['position']), occupied, enemy_pieces, data['color'])

        print(bitboard_to_square(moves))
        socketio.emit('received-moves', {'moves': bitboard_to_square(moves)})

    return ('', 204)


# run app
if __name__ == '__main__':
    socketio.run(app, debug=True)