from flask import Flask, render_template
from flask import request
from models.Song import Song
from models.State import RoomState
from flask_sse import sse
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

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
    sse.publish({"song":request.get_json(force=True)}, type='song')
    return states[room].serialize()

@app.route("/next/<room>")
def next(room):
    sse.publish("next", type='next')
    states[room].next_song()
    return "next"

@app.route("/join/<room>/<user>")
def join_room(room, user):
    if user not in states[room].state['members']:
        states[room].state['members'].append(user)
    return states[room].serialize()

@app.route('/hello')
def publish_hello():
    sse.publish({"message": "Hello!"}, type='greeting')
    return "Message sent!"


@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
