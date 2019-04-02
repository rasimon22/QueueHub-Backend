from flask import Flask
from models.Song import Song

app = Flask(__name__)

@app.route("/join/<room>")
def join_room(room):
    return str(Song(title="A Title", album="An album", uri="URI", user="user"))
@app.route('/create':q)

@app.route("/")
def hello():
    return "Hello World"
