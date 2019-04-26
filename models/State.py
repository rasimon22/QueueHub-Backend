import json
import redis
from redis import RedisError


class RoomState(object):
    def __init__(self, **kwargs):

        self.state = kwargs
        self.state['current_song'] = ''
        if len(self.state['queue']) > 0:
            self.state['current_song'] = self.state['queue'][0]

    def store(self):
        try:
            r = redis.Redis(host="redis://127.0.0.1")
            ret = {"name": self.state['name'], "queue": self.state['queue'], "current_song": self.state['current_song'],
                   "members": self.state['members'], "playback": self.state['playback_status'], "skip_count":
                       self.state['skip_count']}
            r.set(self.state['name'], json.dumps(ret))
            return json.dumps(ret)
        except RedisError:
            return False

    def load(self, name):
        try:
            r = redis.Redis(host="redis://127.0.0.1")
            if r.exists(name):
                self.state = r.get(name)
                return True
            else:
                return False
        except RedisError:
            return False

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
