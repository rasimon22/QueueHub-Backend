import json
class Song:
    def __init__(self, **kwargs):
        self.properties = kwargs
#title
#alabum
#uri
#user
    
    def __str__(self):
        return json.dumps(self.properties)
