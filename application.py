import os

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_socketio import SocketIO, join_room, leave_room
from datetime import datetime

app = Flask(__name__)

# app.config.from_envvar('APP_SETTINGS')

# app.config['FLASK_APP'] = os.environ.get('FLASK_APP')
# app.config['FLASK_DEBUG'] = os.environ.get('FLASK_DEBUG')
app.config["SECRET_KEY"] = 'OCML3BRawWEUeaxcuKHLpw'

socketio = SocketIO(app)


rooms = [ "JavaScript", "Python", "PHP","Java"]
active = {
    "JavaScript": {"No one"},
    "Python": {"No one"},
    "PHP": {"No one"},
    "Java": {"No one"}
}

@app.route("/")
def index():
  
    return render_template('index.html', rooms=rooms, active=active)


@app.route("/chat/", methods=["GET", "POST"])
def chat():

    if request.method == "POST": 
        req = request.form
        try:
            username = req['username']
            room = req['room']
        except:
            print('csjjs')
            return redirect(url_for('clear'))
        addroom = req['addroom']
        submitbutton = req['submitbutton']                
        
        users = active[room]
        
        if submitbutton == "newroom":
            if addroom == "" or (addroom.lower() in (room.lower() for room in rooms)):
                return redirect(url_for('index'))             
            else:      
                rooms.append(addroom)
                return render_template('chat.html', username=username, room=addroom, newroom=1, users=users)
        else:
            if username and room:
                return render_template('chat.html', username=username, room=room, newroom=0, users=users)
            else:
                return redirect(url_for('index'))               


@app.route("/clear")
def clear():
    return render_template('clear.html')  

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(
        data['username'], data['room']))
    active[data['room']].add(data['username'])
    data_user = list(active[data['room']])
    socketio.emit('users_announcement', data_user)
    join_room(data['room'])  # Function present in socket.io
    socketio.emit('join_room_announcement', data)


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent {} in the room {}".format(
        data['username'], data['message'], data['room']))
    socketio.emit('receive_message', data, room=data["room"]) # Argument for socket.io function
    

@socketio.on('new_room')
def handle_new_room_event(data):
    app.logger.info("{} has created new room {}".format(
        data['username'], data['room']))
    new_key = {data['username'], "No one"}
    active[data['room']] = new_key
    # print(active)
    data_user = list(active[data['room']])
    socketio.emit('users_announcement', data_user)
    join_room(data['room'])  # Function present in socket.io
    socketio.emit('new_room_announcement', data)

    
@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    active[data['room']].discard(data['username'])
    # print(active)
    data_user = list(active[data['room']])
    socketio.emit('users_announcement', data_user)
    leave_room(data['room'])  # Function present in socket.io
    socketio.emit('leave_room_announcement', data)