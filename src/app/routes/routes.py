from flask import Blueprint
from game.play import chessGame

bp = Blueprint('main', __name__)


# main page
@bp.route('/chess')
def public():
    chess = chessGame().runGame()
    return chess

@bp.route('/get-moves', methods=['POST'])
def giveMoves():
    recieved_moves = chessGame().giveMoves()
    return recieved_moves

# create move from client
@bp.route('/make_move', methods=['POST'])
def create_move():
    action = chessGame().create_move()
    return action


# reset game sessions
@bp.route('/reset_board', methods=['POST'])
def reset_board():
    rollback = chessGame().reset_board()
    return rollback