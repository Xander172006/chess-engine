from flask_socketio import SocketIO, emit


# server socket handlers
def register_socket_handlers(socketio):
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')