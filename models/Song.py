class Song:
    def __init__(self, **kwargs):
        self.title = kwargs['title']
        self.album = kwargs['album']
        self.uri = kwargs['uri']
        self.user = kwargs['user']
    
    def __str__(self):
        return self.title+ self.album+ self.uri+ self.user
