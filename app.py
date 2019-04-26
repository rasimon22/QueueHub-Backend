from flask import Flask, render_template
from flask import request, make_response
from models.State import RoomState
from flask_cors import CORS
from flask_sse import sse
import redis
import json


app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

states = {}
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')


def send_message(msg, t, ch):
    sse.publish(msg, type=t, channel=ch)

@app.route("/create/<uuid>")
def create_room(uuid):
    r = redis.Redis(host="localhost")
    room = RoomState(name=uuid, room_code=uuid, queue=[], current_song = '',
                      members=[], playback_status="playing", skip_count=0)
    if not room.store():
        return "error"

    return r.get(uuid)


@app.route("/add/<uuid>", methods=['POST'])
def add(uuid):
    r = redis.Redis(host="localhost")
    room = RoomState.load(uuid)
    if room == False:
        return make_response("not found", 400)
    for song in room.state['queue']:
        if song['id'] == request.get_json(force=True)['id']:
            return make_response("duplicate", 400)

    room.add_song(request.get_json(force=True))
    sse.publish({"song": request.get_json(force=True)}, type='song', channel=uuid)
    if not room.store():
        return "error"
    return r.get(uuid)


@app.route("/next/<uuid>")
def next_song(uuid):
    room = RoomState().load(uuid)
    if room == False:
        return make_response("not found", 400)
    sse.publish("next", type='next', channel=uuid)
    room.next_song()
    return room.store()


@app.route("/join/<uuid>/<user>")
def join_room(uuid, user):
    room = RoomState().load(uuid)
    if room == False:
        return make_response("not found", 400)
    if user not in room.state['members']:
        room.state['members'].append(user)
        sse.publish({"user": user}, type="join", channel=uuid)
    return room.store()


@app.route("/pause/<uuid>")
def pause(uuid):
    room = RoomState().load(uuid)
    if room == False:
        return make_response("not found", 400)
    if room.state['playback_status'] == 'playing':
        room.state['playback_status'] = 'paused'
        sse.publish("pause", type='playback', channel=uuid)
    return room.store()


@app.route("/play/<uuid>")
def play(uuid):
    room = RoomState().load(uuid)
    if room == False:
        return make_response("not found", 400)
    if room.state['playback_status'] == 'paused':
        room.state['playback_status'] = 'playing'
        sse.publish("playing", type='playback', channel=uuid)
    return room.store()


@app.route("/skip/<uuid>")
def skip(uuid):
    sse.publish(room.state['skip_count'], type="skip", channel=uuid)
    room = RoomState().load(uuid)
    if room == False:
        return make_response("not found", 400)
    room.next_song()
    return room.store()


@app.route("/<uuid>/<user>/bump/<song_id>")
def bump(uuid, user, song_id):
    sse.publish(song_id, type='bump', channel=uuid)
    room = RoomState().load(uuid)
    if room == False:
        return make_response("not found", 400)
    room.bump_song(song_id)
    return room.store()


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()

