from game import Game
from player import Player
from client import Client

class GameManager:
    def __init__(self):
        self.games = {}
        self.clients = {}

    def initialize_game(self, player):
        new_game = Game(player)
        self.games[new_game.id] = new_game
        return new_game

    def get_game(self, game_id):
        return self.games.get(game_id, None)
    
    def remove_game(self, game_id):
        self.games.pop(game_id, None)
        
    def add_client(self, session_id, player: Player, game_id: str):
        self.clients[session_id] = Client(player, game_id)
        
    def get_player_from_session(self, session_id):
        return self.clients[session_id].player
    
    def set_client(self, session_id, player: Player, game_id: str):
        if session_id not in self.clients:
            self.clients[session_id] = Client(session_id, player, game_id)
        else:
            self.clients[session_id].player = player
            self.clients[session_id].game_id = game_id
        
    def get_game_id(self, session_id):
        return self.clients[session_id].game_id
    
    def remove_client(self, session_id):
        self.clients.pop(session_id, None)
