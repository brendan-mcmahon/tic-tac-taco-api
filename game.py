from game_status import GameStatus
from name_generator import generate_menu_item
from check_winner import check_winner
from player import Player

class Game:
    def __init__(self, player: Player):
        self.id = generate_menu_item()
        self.players = [player]
        self.board = [None] * 9
        self.currentPlayerId = player.id
        self.status = GameStatus.WAITING
        self.winner = None
        self.winningCombination = None
        self.playerMoves = {player.id: []}
        self.isTieGame = False

    def add_player(self, player):
        player.icon = 'o' if len(self.players) == 1 else 'x'
        self.players.append(player)
        self.playerMoves[player.id] = []
        if len(self.players) == 2:
            self.status = GameStatus.PLAYING

    def handle_move(self, index, player_id):
        self.board[index] = player_id
        self.playerMoves[player_id].append(index)
        self.remove_oldest_move(player_id)
        self.currentPlayerId = next(p for p in self.players if p.id != player_id).id
        self.handle_game_end()

    def remove_oldest_move(self, player_id):
        if len(self.playerMoves[player_id]) == 4:
            removeIndex = self.playerMoves[player_id].pop(0)
            self.board[removeIndex] = None

    def handle_game_end(self):
        gameOver = check_winner(self.board)
        if gameOver is not None or None not in self.board:
            if gameOver == "tie game":
                self.isTieGame = True
            else:
                self.winner = gameOver['winner']
                self.winningCombination = gameOver['winning_combination']
            self.status = GameStatus.FINISHED
            self.currentPlayerId = None
    
    def reset_game(self, player):
        self.board = [None] * 9
        self.currentPlayerId = player.id
        self.status = GameStatus.PLAYING
        self.winner = None
        self.winningCombination = None
        self.playerMoves = {player.id: [] for player in self.players}
        self.isTieGame = False

    def to_json(self):
        return {
            'id': self.id,
            'players': [player.to_json() for player in self.players],
            'board': self.board,
            'currentPlayerId': self.currentPlayerId,
            'status': self.status.value,
            'winner': self.winner,
            'winningCombination': self.winningCombination,
            'isTieGame': self.isTieGame,
        }
        