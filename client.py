from player import Player

class Client:
    def __init__(self, player: Player, game_id: str):
        self.player = player
        self.game_id = game_id
    
    def to_json(self):
        return {
            'player': self.player.to_json() if self.player else None,
            'game_id': self.game_id if self.game_id else None,
        }
        