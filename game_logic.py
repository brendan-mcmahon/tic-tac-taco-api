from name_generator import generate_menu_item
from check_winner import check_winner

clients = {}
games = {}

def initialize_game(player):
    player['icon'] = 'x'
    return {
        'id': generate_menu_item(), 
        'players': [player],
        'board': [None]*9,
        'currentPlayerId': player['id'],
        'status': 'waiting',
        'winner': None,
        'winningCombination': None,
        'playerMoves': {player['id']: []}
    }

def add_player_to_game(game, player):
    player['icon'] = 'o' if len(game['players']) == 1 else 'x'
    game['players'].append(player)
    game['playerMoves'][player['id']] = []
    if len(game['players']) == 2:
        game['status'] = 'playing'
        
def handle_move(index, game_id, player_id):
    games[game_id]['board'][index] = player_id
    games[game_id]['playerMoves'][player_id].append(index)
    
    remove_oldest_move(game_id, player_id)

    games[game_id]['currentPlayerId'] = next(player for player in games[game_id]['players'] if player['id'] != player_id)['id']
    
    handle_game_end(game_id, games)
    
def remove_oldest_move(game_id, player_id):
    if len(games[game_id]['playerMoves'][player_id]) == 4:
        removeIndex = games[game_id]['playerMoves'][player_id].pop(0)
        games[game_id]['board'][removeIndex] = None
        
def handle_game_end(game_id, games):
    gameOver = check_winner(games[game_id]['board'])
    
    if (gameOver is not None) or (None not in games[game_id]['board']):
        if (gameOver == "tie game"):
                games[game_id]['isTieGame'] = True
        else:
            games[game_id]['winner'] = gameOver['winner']
            games[game_id]['winningCombination'] = gameOver['winning_combination']
            
        games[game_id]['status'] = 'finished'
        games[game_id]['currentPlayerId'] = None