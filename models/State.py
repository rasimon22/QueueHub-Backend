import json


class RoomState(object):
    def __init__(self, **kwargs):

        self.state = kwargs
        self.state['current_song'] = ''
        if len(self.state['queue']) > 0:
            self.state['current_song'] = self.state['queue'][0]

    def serialize(self):
        ret = {"queue": self.state['queue'], "current_song": self.state['current_song'],
               "members": self.state['members'], "playback": self.state['playback_status']}

        return json.dumps(ret)

    def add_song(self, song):
        self.state['queue'].append(song)
        if self.state['current_song'] == '':
            self.state['current_song'] = self.state['queue'].pop(0)

    def add_member(self, member):
        self.state['members'].append(member)
    
    def next_song(self):
        if len(self.state['queue']) > 0:
            self.state['current_song'] = self.state['queue'].pop(0)
            return self.state['current_song']
        return self.state['current_song']

    def bump_song(self, song_id):
        for idx, s in enumerate(self.state['queue']):
            song = json.loads(s)
            if song_id == song['id']:
                song['bumps'] += 1
                s = json.dumps(song)
                if len(self.state['queue']) > 1 and song['bumps'] > json.dumps(self.state['queue'][idx - 1])['bumps']:
                    self.state['queue'][idx - 1], s = s, self.state['queue'][idx - 1]
        return self.state['queue']

