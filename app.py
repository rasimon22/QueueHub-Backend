from flask import Flask, render_template
from flask import request, make_response
from models.Song import Song
from models.State import RoomState
from flask_cors import CORS
from flask_sse import sse
import json

app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

states = {}
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')


@app.route("/create/<room>")
def create_room(room):
    songs = []
    states[room] = RoomState(room_code=room, queue=songs,
                             playback_status="playing", members=['rasimon'])

    return states[room].serialize()


@app.route("/add/<room>", methods=['POST'])
def add(room):
    states[room].add_song(request.get_json(force=True))
    sse.publish({"song": request.get_json(force=True)}, type='song', channel=str(room))
    return states[room].serialize()


@app.route("/next/<room>")
def next(room):
    sse.publish("next", type='next', channel=str(room))
    states[room].next_song()
    return "next"


@app.route("/join/<room>/<user>")
def join_room(room, user):
    if room not in states.keys():
        return make_response("not found", 400)
    if user not in states[room].state['members']:
        states[room].state['members'].append(user)
    return states[room].serialize()


@app.route("/pause/<room>")
def pause(room):
    if states[room].state['playback_status'] == 'playing':
        states[room].state['playback_status'] = 'paused'
        sse.publish("pause", type='playback', channel=str(room))
    return "pause"


@app.route("/play/<room>")
def play(room):
    if states[room].state['playback_status'] == 'paused':
        states[room].state['playback_status'] = 'playing'
        sse.publish("playing", type='playback', channel=str(room))
    return "play"


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()

