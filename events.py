from flask_socketio import emit, join_room, leave_room
from flask import request
from game_logic import initialize_game, handle_move, add_player_to_game, games, clients

def update_dashboard():
    emit('update_dashboard', {'clients': clients, 'games': games}, broadcast=True)

def log(message):
    emit('log', message, broadcast=True)

def connect():
    session_id = request.sid
    clients[session_id] = {'player': None, 'game_id': None}
    print('Client connected', session_id)
    log(f"Client connected: {session_id}")
    update_dashboard()
        
def disconnect():
    session_id = request.sid
    player_info = clients.pop(session_id, None)
    if player_info and player_info['game_id'] and player_info['player']:
        leave_game()
        update_dashboard()
        
def create_game(data):
    player = data.get('player')
    log(f"Creating game for player: {player['name']}")
    game = initialize_game(player)
    log(f"Game initialized: {game['id']}")
    session_id = request.sid
    games[game['id']] = game
    clients[session_id] = {'player': player, 'game_id': game['id']}
    join_room(game['id'])
    emit('gameState', game, room=game['id'])
    update_dashboard()

def join_game(data):
    session_id = request.sid
    game_id = data.get('gameId')
    player = data.get('player')
    game = games.get(game_id)
    
    if not game:
        emit('gameNotFound', room=session_id)
        log(f"Game not found: {game_id}")
        return
        
    if len(game['players']) >= 2:
        emit('gameFull', room=game_id)
        log(f"Game is full: {game_id}")
        return
    
    add_player_to_game(game, player)
    log(f"Player {player['name']} joined game {game_id}")
    
    clients[session_id] = {'player': player, 'game_id': game['id']}

    join_room(game_id)
    emit('gameState', games[game_id], room=game_id)
    update_dashboard()
    
def make_move(data):
    game_id = data.get('gameId')
    player_id = data.get('playerId')
    index = data.get('index')
    if game_id in games:
        handle_move(index, game_id, player_id)
        emit('gameState', games[game_id], room=game_id)
    update_dashboard()

def leave_game():
    sid = request.sid
    game_id = clients[sid]['game_id']
    games.pop(game_id)
    emit('gameDeleted', room=game_id)
    leave_room(game_id)
    update_dashboard()
        
def rematch(data):
    game_id = data.get('gameId')
    if game_id not in games:
        emit('error', {'message': 'Game not found.'}, room=request.sid)
        return
    
    player = data.get('player')
    if not player:
        emit('error', {'message': 'Player data is missing.'}, room=request.sid)
        return

    if not any(p['id'] == player['id'] for p in games[game_id]['players']):
        emit('error', {'message': 'Player not part of the game.'}, room=request.sid)
        return

    try:
        otherPlayer = next(p for p in games[game_id]['players'] if p['id'] != player['id'])
        games[game_id]['board'] = [None]*9
        games[game_id]['currentPlayerId'] = player['id']
        games[game_id]['status'] = 'playing'
        games[game_id]['winner'] = None
        games[game_id]['winningCombination'] = None
        games[game_id]['playerMoves'][player['id']] = []
        games[game_id]['playerMoves'][otherPlayer['id']] = []
        games[game_id]['isTieGame'] = False

        emit('gameState', games[game_id], room=game_id)
        update_dashboard()
    except Exception as e:
        print(f"Error during rematch: {e}")
        emit('error', {'message': 'Failed to setup rematch.'}, room=game_id)


def setup_socket_events(socketio):
    @socketio.on('connect')
    def on_connect(): connect()
    @socketio.on('disconnect')
    def on_disconnect(): disconnect()
    @socketio.on('createGame')
    def on_create(data): create_game(data)
    @socketio.on('joinGame')
    def on_join(data): join_game(data)
    @socketio.on('makeMove')
    def on_make_move(data): make_move(data)
    @socketio.on('leaveGame')
    def on_leave_game(data): leave_game()
    @socketio.on('rematch')
    def on_rematch(data): rematch(data)