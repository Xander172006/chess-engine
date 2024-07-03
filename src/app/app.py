from flask import Flask, session
from flask_socketio import SocketIO
from routes.routes import bp as route_bp

# create app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
SocketIO = SocketIO(app)


# register blueprints
app.register_blueprint(route_bp)


# run app
if __name__ == '__main__':
    SocketIO.run(app, debug=True)