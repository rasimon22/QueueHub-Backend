import json


class RoomState(object):
    def __init__(self, **kwargs):
        # self.queue = kwargs['queue']
        # self.members = kwargs['members']
        # kself.playback_status = kwargs['playback_status']
        # self.room_code = kwargs['room_code']
        self.state = kwargs
        self.state['current_song'] = ''
        if len(self.state['queue']) > 0:
            self.state['current_song'] = self.state['queue'][0]

    def serialize(self):
        ret = {"queue":self.state['queue'], "current_song": self.state['current_song'],"members":self.state['members'], "playback":self.state['playback_status']}

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

