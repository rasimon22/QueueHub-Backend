class State:
    def __init__(self, **kwargs):
        self.queue = kwargs['queue']
        self.current_song = kwargs['current_song']
        self.members = kwargs['members']
        self.playback_status = kwargs['playback_status']
        self.room_code = kwargs['room_code']
