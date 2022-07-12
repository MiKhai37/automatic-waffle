from uuid import uuid4
from scrabble_python.items.tile import Tile


class Player:
    def __init__(self, player_id: str = None, rack: list[Tile] = None) -> None:
        if player_id is None:
            player_id = str(uuid4())
        self.id = player_id
        if rack is None:
            rack = []
        self.rack = rack
