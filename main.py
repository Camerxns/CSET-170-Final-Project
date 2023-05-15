from website import create_app

app, socketio = create_app()

if __name__ == '__main__':
    with app.app_context():
        socketio.run(app, debug=True, use_reloader=True)
