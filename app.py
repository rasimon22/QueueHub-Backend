from flask import Flask
from models.Song import Song
from models.State import room_state

app = Flask(__name__)

states = {}

@app.route("/create/<room>")
def create_room(room):
    songs = []
    for x in range(10):
        songs.append(Song(title="Sweet Child O' Mine", album="Appetite For Destruction",
            uri="a url", user="rasimon"))
    states[room] = room_state(room_code=room, queue=songs,
            playback_status="playing", members='rasimon')
    return states[room]
@app.route("/join/<room>")
def join_room(room):
    return str(states[room])
@app.route('/create')

@app.route("/")
def hello():
    return "Hello World"
app.run(host="0.0.0.0")
