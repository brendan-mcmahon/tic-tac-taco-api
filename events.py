from flask import request
from flask_socketio import join_room, leave_room, emit

from game import Game
from game_manager import GameManager
from player import Player

from functools import wraps

game_manager = GameManager()

def update_dashboard():
    clients_json = {client_id: client.to_json() for client_id, client in game_manager.clients.items()}
    games_json = {game_id: game.to_json() for game_id, game in game_manager.games.items()}
    emit('update_dashboard', {'clients': clients_json, 'games': games_json}, broadcast=True)

def log(message: str):
    emit('log', message, broadcast=True)
    
def emitGame(game: Game):
    _game = game.to_json() if game else None
    room = request.sid if game is None else game.id
    emit('gameState', _game, room=room)

def emitError(message: str):
    emit('error', {'message': message}, room=request.sid)
    
def log_and_update_dashboard(event):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            result = func(*args, **kwargs)
            update_dashboard()
            log(f"{event}: {result}")
            return result
        return wrapped
    return decorator

@log_and_update_dashboard("Client Connected")
def connect(*args, **kwargs):
    session_id = request.sid
    game_manager.add_client(session_id, None, None)
    return session_id

@log_and_update_dashboard("Client Disconnected")
def disconnect(*args, **kwargs):
    session_id = request.sid
    player = game_manager.get_player_from_session(session_id)
    if player:
        leave_game()
        return player.name
        
@log_and_update_dashboard("Game Created")
def create_game(data):
    player = Player(data.get("player"))
    player.icon = "x"
    session_id = request.sid
    game = game_manager.initialize_game(player)
    game_manager.set_client(session_id, player, game.id)
    join_room(game.id)
    emitGame(game)
    return f"Game for player {player.name} initialized with ID {game.id}"

@log_and_update_dashboard("Game Joined")
def join_game(data):
    session_id = request.sid
    game_id = data.get("gameId")
    player = Player(data.get("player"))
    game = game_manager.get_game(game_id)
    
    if not game:
        emitError("gameNotFound")
        return "Game not found" + game_id
        
    if len(game.players) >= 2:
        emitError("gameFull")
        return "Game is full" + game_id
    
    game.add_player(player)
    
    game_manager.set_client(session_id, player, game.id)

    join_room(game_id)
    emitGame(game)
    return f"Player {player.name} joined game {game_id}"
    
@log_and_update_dashboard("Make Move")
def make_move(data):
    game_id = data.get("gameId")
    player_id = data.get("playerId")
    index = data.get("index")
    game = game_manager.get_game(game_id)
    game.handle_move(index, player_id)
    emitGame(game)
    return f"Player {player_id} moved to {index} in game {game_id}"

@log_and_update_dashboard("Leave Game")
def leave_game(*args, **kwargs):
    sid = request.sid
    game_id = game_manager.clients[sid].game_id
    game_manager.remove_game(game_id)
    emitGame(None)
    leave_room(game_id)
    return f"Player left game {game_id}"

@log_and_update_dashboard("Rematch")
def rematch(data):
    game_id = data.get("gameId")
    game = game_manager.get_game(game_id)
    if game is None:
        emitError("Game not found.")
        return "Game not found" + game_id
    
    player = Player(data.get("player"))
    if not player:
        emitError("Player data is missing.")
        return "Player data is missing"

    if not any(p.id == player.id for p in game.players):
        emitError("Player not part of the game.")
        return "Player not part of the game" + player.id

    try:
        game.reset_game(player)
        emitGame(game)
        return "Rematch setup successfully" + game_id
    except Exception as e:
        print(f"Error during rematch: {e}")
        emitError("Failed to setup rematch.")
        return "Failed to setup rematch" + game_id

def setup_socket_events(socketio):
    socketio.on("connect")(connect)
    socketio.on("disconnect")(disconnect)
    socketio.on("createGame")(create_game)
    socketio.on("joinGame")(join_game)
    socketio.on("makeMove")(make_move)
    socketio.on("leaveGame")(leave_game)
    socketio.on("rematch")(rematch)
