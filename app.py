from flask import Flask, render_template
from flask import request, make_response
from models.State import RoomState
from flask_cors import CORS
from flask_sse import sse
import redis


app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

states = {}
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')


@app.route("/create/<room>")
def create_room(room):
    r = redis.Redis(host="redis://localhost")
    _room = RoomState(name=room, room_code=room, queue=[],
                      playback_status="playing", members=['rasimon'],
                      skip_count=0)
    _room.store()

    return r.get(room)



@app.route("/add/<uuid>", methods=['POST'])
def add(uuid):
    room = RoomState()
    if not room.load(uuid):
        return make_response("not found", 400)
    for song in room.state['queue']:
        if song['id'] == request.get_json(force=True)['id']:
            return make_response("duplicate", 400)

        room.add_song(request.get_json(force=True))
        sse.publish({"song": request.get_json(force=True)}, type='song', channel=str(room))
    return room.store()


@app.route("/next/<uuid>")
def next_song(uuid):
    room = RoomState()
    if not room.load(uuid):
        return make_response("not found", 400)
    sse.publish("next", type='next', channel=str(room))
    room.next_song()
    return room.store()


@app.route("/join/<uuid>/<user>")
def join_room(uuid, user):
    room = RoomState()
    if not room.load(uuid):
        return make_response("not found", 400)
    if user not in room.state['members']:
        room.state['members'].append(user)
        sse.publish({"user": user}, type="join", channel=str(room))
    return room.store()


@app.route("/pause/<uuid>")
def pause(uuid):
    room = RoomState()
    if not room.load(uuid):
        return make_response("not found", 400)
    if room.state['playback_status'] == 'playing':
        room.state['playback_status'] = 'paused'
        sse.publish("pause", type='playback', channel=str(room))
    return room.store()


@app.route("/play/<uuid>")
def play(uuid):
    room = RoomState()
    if not room.load(uuid):
        return make_response("not found", 400)
    if room.state['playback_status'] == 'paused':
        room.state['playback_status'] = 'playing'
        sse.publish("playing", type='playback', channel=str(room))
    return room.store()


@app.route("/skip/<uuid>")
def skip(uuid):
    room = RoomState()
    if not room.load(uuid):
        return make_response("not found", 400)
    room.state['skip_count'] += 1
    sse.publish(room.state['skip_count'], type="skip", channel=str(room))
    return room.store()


@app.route("/<uuid>/<user>/bump/<song_id>")
def bump(uuid, user, song_id):
    room = RoomState()
    if not room.load(uuid):
        return make_response("not found", 400)
    sse.publish(song_id, type='bump', channel=str(room))
    room.bump_song(song_id)
    return room.store()


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()

