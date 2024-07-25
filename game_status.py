from enum import Enum

class GameStatus(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"