from flask import Flask, render_template
from flask import request
from models.Song import Song
from models.State import RoomState
from flask_sse import sse
import json

app = Flask(__name__)

states = {}
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')


@app.route("/create/<room>")
def create_room(room):
    songs = []
    for x in range(10):
        songs.append(Song(title="Homecoming", album="Graduation",
                          uri="a url", user="rasimon"))
    states[room] = RoomState(room_code=room, queue=songs,
                             playback_status="playing", members=['rasimon'])
    states[room].add_song(Song(title="Aint No Rest for the Wicked", album="Album_",
                          uri="another_url", user="rasimon"))
    return states[room].serialize()


@app.route("/add/<room>", methods=['POST'])
def add(room):
    #states[room].add_song(request.form['song'])
    sse.publish({"song":json.dumps(request.form['song'])}, type='song')
    return states[room].serialize()


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
