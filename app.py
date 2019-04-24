from flask import Flask, render_template
from flask import request, make_response
from models.Song import Song
from models.State import RoomState
from flask_cors import CORS
from flask_sse import sse
from multiprocessing import Lock
import datetime
import json

app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

states = {}
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

state_lock = Lock()

@app.route("/create/<room>")
def create_room(room):
    state_lock.acquire()
    try:
        states[room] = RoomState(room_code=room, queue=[],
                                 playback_status="playing", members=['rasimon'],
                                 skip_count=0)
    finally:
        state_lock.release()

    return states[room].serialize()


@app.route("/add/<room>", methods=['POST'])
def add(room):
    if room not in states.keys():
        return make_response("not found", 400)
    state_lock.acquire()
    try:
        for song in states[room].state['queue']:
            if song['id'] == request.get_json(force=True)['id']:
                return make_response("duplicate", 400)

        states[room].add_song(request.get_json(force=True))
    finally:
        state_lock.release()
    sse.publish({"song": request.get_json(force=True)}, type='song', channel=str(room))
    return states[room].serialize()


@app.route("/next/<room>")
def next(room):
    if room not in states.keys():
        return make_response("not found", 400)
    sse.publish("next", type='next', channel=str(room))
    state_lock.acquire()
    try:
        states[room].next_song()
    finally:
        state_lock.release()
    return "next"


@app.route("/join/<room>/<user>")
def join_room(room, user):
    if room not in states.keys():
        return make_response("not found", 400)
    state_lock.acquire()
    try:
        if user not in states[room].state['members']:
            states[room].state['members'].append(user)
    finally:
        state_lock.release()
    sse.publish({"user": user}, type="join", channel=str(room))
    return states[room].serialize()


@app.route("/pause/<room>")
def pause(room):
    if room not in states.keys():
        return make_response("not found", 400)
    state_lock.acquire()
    try:
        if states[room].state['playback_status'] == 'playing':
            states[room].state['playback_status'] = 'paused'
            sse.publish("pause", type='playback', channel=str(room))
    finally:
        state_lock.release()
    return "pause"


@app.route("/play/<room>")
def play(room):
    if room not in states.keys():
        return make_response("not found", 400)
    state_lock.acquire()
    try:
        if states[room].state['playback_status'] == 'paused':
            states[room].state['playback_status'] = 'playing'
            sse.publish("playing", type='playback', channel=str(room))
    finally:
        state_lock.release()
    return "play"


@app.route("/skip/<room>")
def skip(room):
    if room not in states.keys():
        return make_response("not found", 400)
    state_lock.acquire()
    try:
        states[room].state['skip_count'] += 1
        sse.publish(states[room].state['skip_count'], type="skip", channel=str(room))
    finally:
        state_lock.release()
    return str(states[room].state['skip_count'])


@app.route("/<room>/<user>/bump/<song_id>")
def bump(room, user, song_id):
    if room not in states.keys():
        return make_response("not found", 400)
    state_lock.acquire()
    try:
        states[room].bump_song(song_id)
        sse.publish(song_id, type='bump', channel=str(room))
    finally:
        state_lock.release()
    return song_id


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()

