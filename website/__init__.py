from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from environs import Env
from flask_socketio import SocketIO

env = Env()
env.read_env()

db = SQLAlchemy()
MYSQL_USERNAME = env("MYSQL_USERNAME")
MYSQL_PASSWORD = env("MYSQL_PASSWORD")
MYSQL_HOST = env("MYSQL_HOST")
MYSQL_PORT = env.int("MYSQL_PORT")
MYSQL_DATABASE = "CSET_180_FINAL_PROJECT"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = env("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    app.config['UPLOAD_FOLDER'] = "static/uploads/"
    # app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['FLASK_SOCKETIO_ENABLED'] = True


    db.init_app(app)

    from .views import views
    from .auth import auth
    from .vendor import vendor
    from .admin import admin
    from .customer import customer
    from .chatroom import chat, create_socketio


    socketio = create_socketio(app)

    from .chatroom import chat

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(vendor, url_prefix="/vendor/")
    app.register_blueprint(admin, url_prefix="/admin/")
    app.register_blueprint(customer, url_prefix="/admin")
    app.register_blueprint(chat, url_prefix="/")

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app, socketio
