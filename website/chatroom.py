from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
from flask import current_app as app
import random
from .models import ChatMessage, Chat
from . import db

socketio = SocketIO()

chat = Blueprint('chat', __name__)


rooms = {}


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
        return redirect(url_for("chat.room"))

    return render_template("chat2.html")


@chat.route("/chat/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("chat.home"))

    return render_template("chatroom.html", code=room, messages=rooms[room]["messages"])



@socketio.on("message")
def message(data):
    name = session.get('name')
    room = session.get("room")
    message = data["data"]
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")
    chat_id = Chat(chat_id=room)
    chat_message = ChatMessage(chat_id=room, user_id=name, message=message)
    db.session.add(chat_id)
    db.session.commit()
    db.session.add(chat_message)
    db.session.commit()



@socketio.on("connect")
def connect(auth):
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


if __name__ == "__main__":
    socketio.init_app(app, debug=True)
    socketio.run(app, debug=True)
