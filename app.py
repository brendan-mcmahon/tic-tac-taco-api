import os
from flask import Flask, request  # Make sure 'request' is imported here
from flask_socketio import SocketIO, emit, join_room, leave_room
from name_generator import generate_menu_item
from check_winner import check_winner

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*")

clients = {}
games = {}

@app.route('/')
def index():
    return "Tac Server is running!"

@socketio.on('connect')
def test_connect():
    session_id = request.sid
    clients[session_id] = {'player': None, 'game_id': None}
    print('Client connected', session_id)

@socketio.on('disconnect')
def test_disconnect():
    session_id = request.sid
    player_info = clients.pop(session_id, None)
    if player_info and player_info['game_id'] and player_info['player']:
        game_id = player_info['game_id']
        player_name = player_info['player']['name']
        print(f"Client disconnected: {player_name}")
        emit('playerDisconnected', {'player_name': player_name}, room=game_id)


@socketio.on('makeMove')
def handle_move(data):
    game_id = data.get('gameId')
    player_id = data.get('playerId')
    index = data.get('index')
    print("bug", data)
    if game_id in games:
        games[game_id]['board'][index] = player_id
        games[game_id]['currentPlayerId'] = next(player for player in games[game_id]['players'] if player['id'] != player_id)['id']
        gameOver = check_winner(games[game_id]['board'])
        print(gameOver)
        
        if (gameOver is not None) or (None not in games[game_id]['board']):
            if (gameOver == "tie game"):
                games[game_id]['isTieGame'] = True
            else:
                games[game_id]['winner'] = gameOver['winner']
                games[game_id]['winningCombination'] = gameOver['winning_combination']
            games[game_id]['status'] = 'finished'
            games[game_id]['currentPlayerId'] = None
        
        emit('gameState', games[game_id], room=game_id)

@socketio.on('createGame')
def on_create(data):
    game_id = generate_menu_item()
    player = data.get('player')
    player['icon'] = 'x'
    print('player', player)
    session_id = request.sid
    games[game_id] = {
        'id': game_id, 
        'players': [player],
        'board': [None]*9, 
        'currentPlayerId': player['id'],
        'status': 'waiting',
        'winner': None,
        'winningCombination': None
    }
    clients[session_id]['player'] = player
    clients[session_id]['game_id'] = game_id
    join_room(game_id)
    emit('gameState', games[game_id], room=game_id)

@socketio.on('joinGame')
def on_join(data):
    game_id = data.get('gameId')
    player = data.get('player')
    session_id = request.sid
    if game_id not in games:
        emit('gameNotFound', room=session_id)
    elif len(games[game_id]['players']) >= 2:
        emit('gameFull', room=game_id)
    else:
        player['icon'] = 'o'
        games[game_id]['players'].append(player)
        games[game_id]['status'] = 'playing'
    clients[session_id]['player'] = player
    clients[session_id]['game_id'] = game_id
    join_room(game_id)
    emit('gameState', games[game_id], room=game_id)
    
@socketio.on('leaveGame')
def on_leave_game(data):
    # remove the game from the games dictionary
    # remove the client from the clients dictionary
    # leave the room
    sid = request.sid
    game_id = clients[sid]['game_id']
    games.pop(game_id)
    emit('gameDeleted', room=game_id)
    leave_room(game_id)
        
    
@socketio.on('rematch')
def on_rematch(data):
    game_id = data.get('gameId')
    player = data.get('player')
    games[game_id]['board'] = [None]*9
    games[game_id]['currentPlayerId'] = player['id']
    games[game_id]['status'] = 'playing'
    games[game_id]['winner'] = None
    games[game_id]['winningCombination'] = None
    emit('gameState', games[game_id], room=game_id)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
