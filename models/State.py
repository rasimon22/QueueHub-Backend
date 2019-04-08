import json


class RoomState(object):
    def __init__(self, **kwargs):
        # self.queue = kwargs['queue']
        # self.members = kwargs['members']
        # kself.playback_status = kwargs['playback_status']
        # self.room_code = kwargs['room_code']
        self.state = kwargs
        self.state['current_song'] = self.state['queue'][0]

    def serialize(self):
        queue = [s.properties for s in self.state['queue']]
        ret = {"queue":queue, "members":self.state['members'], "playback":self.state['playback_status']}

        return json.dumps(ret)

    def add_song(self, song):
        self.state['queue'].append(song)

    def add_member(self, member):
        self.state['members'].append(member)


