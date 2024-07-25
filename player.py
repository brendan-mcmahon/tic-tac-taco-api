class Player:
    def __init__(self, dict):
        self.id = dict["id"]
        self.name = dict["name"]
        self.icon = dict["icon"]
        
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
        }
        