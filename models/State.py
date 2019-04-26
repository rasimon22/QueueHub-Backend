import json
import redis
from redis import RedisError


class RoomState(object):
    def __init__(self, **kwargs):
        if not "json" in kwargs.keys():
            self.state=kwargs
        else:
            self.state=kwargs['json']

    def store(self):
        try:
            r = redis.Redis(host="localhost")
            ret = {"name": self.state['name'], "queue": self.state['queue'], "current_song": self.state['current_song'],
                   "members": self.state['members'], "playback_status": self.state['playback_status'], "skip_count": self.state['skip_count']}
            r.delete(self.state['name'])
            r.set(self.state['name'],json.dumps(ret))
            return json.dumps(ret)
        except RedisError:
            return False

    @staticmethod
    def load(name):
        try:
            r = redis.Redis(host="localhost")
            if r.exists(name):
                return RoomState(json=json.loads(r.get(name).decode("utf-8")))
            else:
                return False
        except:
            pass

    def add_song(self, song):
        self.state['queue'].append(song)
        if self.state['current_song'] == '':
            self.state['current_song'] = self.state['queue'].pop(0)

    def add_member(self, member):
        self.state['members'].append(member)

    def next_song(self):
        if len(self.state['queue']) > 0:
            self.state['current_song'] = self.state['queue'].pop(0)
            self.state['skip_count'] = 0
            return self.state['current_song']
        return self.state['current_song']

    def bump_song(self, song_id):
        for idx, song in enumerate(self.state['queue']):
            if song_id == song['id']:
                song['bumps'] += 1
                if not all(self.state['queue'][i]['bumps'] >= self.state['queue'][i + 1]['bumps']
                           for i in range(len(self.state['queue']) - 1)):
                    self.state['queue'].sort(key=lambda x: x['bumps'], reverse=True)

        return self.state['queue']
