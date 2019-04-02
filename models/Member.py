class Member:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.id = kwargs['id']
        self.spotify_user = kwargs['spotify_user']
