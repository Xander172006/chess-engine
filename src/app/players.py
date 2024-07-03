# handle player turns
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