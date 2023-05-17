from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from .models import ChatMessage, Chat
from . import db, create_app
import datetime

chat = Blueprint('chat', __name__)

rooms = {}
messages = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += str(random.randint(0, 9))

        if code not in rooms:
            break

    return code


@chat.route("/chat", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("chat2.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("chat2.html", error="Please enter a room code.", code=code, name=name)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("chat2.html", error="Room does not exist.", code=code, name=name)

        session["room"] = room
        session["name"] = name
        print(f"{room}, {session.get('name')}")
        return redirect(url_for("chat.chatroom", room=room))

    return render_template("chat2.html")


@chat.route("/chat/<room>", methods=["POST", "GET"])
def chatroom(room):
    if room not in rooms:
        return render_template("chatroom.html")
    messages = rooms[room]["messages"]
    return render_template("chatroom.html", room=room, messages=messages)

def create_socketio(app):
    socketio = SocketIO(app)

    @socketio.on("message")
    def message(data):
        room = data["room"]
        name = data["name"]
        message = data["message"]

        # Initialize an empty list if the room is not present in the messages dictionary
        if room not in messages:
            messages[room] = []

        messages[room].append({"name": name, "message": message})
        print(f"{message} sent by: {name} in room: {room}")
        socketio.emit("message", {"name": name, "message": message}, room=room)

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_div = "<div class='text'><span><strong>{}</strong>: {}</span><span class='muted'>{}</span></div>".format(name, message, current_time)
        socketio.emit("display_message", message_div, room=room)
        chats_add = Chat(chat_id=room)
        chat_message = ChatMessage(chat_id=room, user_id=name, message=message)
        db.session.add(chats_add)
        db.session.commit()
        db.session.add(chat_message)
        db.session.commit()



    @socketio.on("connect")
    def connect():
        room = session.get("room")
        name = session.get("name")
        if not room or not name:
            return
        if room not in rooms:
            leave_room(room)
            return

        join_room(room)
        send({"name": name, "message": "has entered the room"}, to=room)
        rooms[room]["members"] += 1
        print(f"{name} joined room {room}")

    @socketio.on("disconnect")
    def disconnect():
        room = session.get("room")
        name = session.get("name")
        leave_room(room)

        if room in rooms:
            rooms[room]["members"] -= 1
            if rooms[room]["members"] <= 0:
                del rooms[room]

        send({"name": name, "message": "has left the room"}, to=room)
        print(f"{name} has left the room {room}")

    return socketio
