from website import create_app
from flask_socketio import SocketIO

app = create_app()
socketio = SocketIO()

socketio.init_app(app)


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app, debug=True, use_reloader=True)