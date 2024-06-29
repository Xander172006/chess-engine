from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit

from moves import *
from bitboard import *


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


# initialize game sessions
def initialize_game_state():
    if 'game_state' not in session:
        session['game_state'] = {
            'WHITE_PAWNS': WHITE_PAWNS,
            'WHITE_KNIGHTS': WHITE_KNIGHTS,
            'WHITE_BISHOPS': WHITE_BISHOPS,
            'WHITE_ROOKS': WHITE_ROOKS,
            'WHITE_QUEEN': WHITE_QUEEN,
            'WHITE_KING': WHITE_KING,
            'BLACK_PAWNS': BLACK_PAWNS,
            'BLACK_KNIGHTS': BLACK_KNIGHTS,
            'BLACK_BISHOPS': BLACK_BISHOPS,
            'BLACK_ROOKS': BLACK_ROOKS,
            'BLACK_QUEEN': BLACK_QUEEN,
            'BLACK_KING': BLACK_KING
        }
        session['turn_count'] = 0
        session['player_turn'] = 'white'
        session['store_pieces'] = {
            'white': [],
            'black': []
        }
        session.modified = True

    global bitboard_pieces
    bitboard_pieces = {
            'white_pawns': bitboard_to_array(session['game_state']['WHITE_PAWNS']),
            'white_knights': bitboard_to_array(session['game_state']['WHITE_KNIGHTS']),
            'white_bishops': bitboard_to_array(session['game_state']['WHITE_BISHOPS']),
            'white_rooks': bitboard_to_array(session['game_state']['WHITE_ROOKS']),
            'white_queen': bitboard_to_array(session['game_state']['WHITE_QUEEN']),
            'white_king': bitboard_to_array(session['game_state']['WHITE_KING']),
            'black_pawns': bitboard_to_array(session['game_state']['BLACK_PAWNS']),
            'black_knights': bitboard_to_array(session['game_state']['BLACK_KNIGHTS']),
            'black_bishops': bitboard_to_array(session['game_state']['BLACK_BISHOPS']),
            'black_rooks': bitboard_to_array(session['game_state']['BLACK_ROOKS']),
            'black_queen': bitboard_to_array(session['game_state']['BLACK_QUEEN']),
            'black_king': bitboard_to_array(session['game_state']['BLACK_KING']),
    }



# create move event
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
            validation, message = validateMove(action, moves, game_state, occupied)
            if validation:
                session['game_state'] = game_state
                session['turn_count'] = turn_count + 1
                session['player_turn'] = 'black' if player_turn == 'white' else 'white'
                session.modified = True
                socketio.emit('move-made', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color']})
            else:
                # invalid move
                socketio.emit('invalid-move', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color'], 'message': message})
        else:
            # wrong players turn
            socketio.emit('wrong-turn', {'position': action['position'], 'placement': action['placement'], 'name': action['name'], 'color': action['color']})
    return ('', 204)


# reset board
@app.route('/reset-board', methods=['POST'])
def reset_board():
    # reset sessions
    session.pop('game_state', None)
    session.pop('player_turn', None)
    session.pop('store_pieces', None)
    initialize_game_state()
    game_state = session['game_state']

    pieces_board = bitboard_pieces

    return jsonify(pieces_board)


# chessboard operator
def chessboard(game_state, playerTurn):
    # pieces
    global pieces
    pieces = playerTurnHandling(game_state, playerTurn)

    # occupied squares
    global occupied
    occupied = (game_state['WHITE_PAWNS'] | game_state['WHITE_KNIGHTS'] | game_state['WHITE_BISHOPS'] | game_state['WHITE_ROOKS'] | 
                game_state['WHITE_QUEEN'] | game_state['WHITE_KING'] | game_state['BLACK_PAWNS'] | game_state['BLACK_KNIGHTS'] | 
                game_state['BLACK_BISHOPS'] | game_state['BLACK_ROOKS'] | game_state['BLACK_QUEEN'] | game_state['BLACK_KING'])
    
    # generated moves
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
    pieces_board = bitboard_pieces

    return board, pieces_board


# give correct pieces to the player
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
            'white_pawns': game_state['WHITE_PAWNS'],
            'white_knights': game_state['WHITE_KNIGHTS'],
            'white_bishops': game_state['WHITE_BISHOPS'],
            'white_rooks': game_state['WHITE_ROOKS'],
            'white_queen': game_state['WHITE_QUEEN'],
            'white_king': game_state['WHITE_KING'],
            'pawns': game_state['BLACK_PAWNS'],
            'knights': game_state['BLACK_KNIGHTS'],
            'bishops': game_state['BLACK_BISHOPS'],
            'rooks': game_state['BLACK_ROOKS'],
            'queen': game_state['BLACK_QUEEN'],
            'king': game_state['BLACK_KING'],
    }

    return pieces


# gives the moves to the client-side
@app.route('/get-moves', methods=['POST'])
def get_moves():
    data = request.get_json()

    piece_moves = handle_moves(data['name'], data['color'], data['position'])

    socketio.emit('received-moves', {'moves': piece_moves})

    return ('', 204)


# returns the generated moves
def handle_moves(piece, color, position):
    white_pieces = pieces.get('white_pawns', 0) | pieces.get('white_knights', 0) | pieces.get('white_bishops', 0) | pieces.get('white_rooks', 0) | pieces.get('white_queen', 0) | pieces.get('white_king', 0)
    black_pieces = pieces.get('black_pawns', 0) | pieces.get('black_knights', 0) | pieces.get('black_bishops', 0) | pieces.get('black_rooks', 0) | pieces.get('black_queen', 0) | pieces.get('black_king', 0)

    enemy_pieces = black_pieces if color == 'white' else white_pieces
    position_bitboard = create_bitboard(position)

    move_generators = {
        'pawns': generate_pawn_moves,
        'knights': generate_knight_moves,
        'bishops': generate_bishop_moves,
        'rooks': generate_rook_moves,
        'queen': generate_queen_moves,
        'king': generate_king_moves,
    }

    for key, move_generator in move_generators.items():
        if key in piece:
            if key == 'pawns':
                moves = move_generator(position_bitboard, occupied, enemy_pieces, color)
            elif key == 'knights':
                moves = move_generator(position_bitboard, occupied, enemy_pieces)
            else:
                moves = move_generator(from_bitboard_to_chess_position(position_bitboard), occupied, enemy_pieces)
            break

    return bitboard_to_square(moves)


# run the engine
@app.route('/')
def runEngine():
    initialize_game_state()
    game_state = session['game_state']

    playerTurn = session.get('player_turn', 'white')
    board, pieces_board = chessboard(game_state, playerTurn)
    
    return render_template('chessboard.html', board=board, pieces=pieces_board, playerTurn=playerTurn)


# run app
if __name__ == '__main__':
    socketio.run(app, debug=True)