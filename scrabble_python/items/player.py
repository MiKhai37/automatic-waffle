from uuid import uuid4
from .tile import Tile


class Player:
    def __init__(self, player_id_name: str = None, rack: list[Tile] = None) -> None:
        self.id = player_id_name
        if self.id is None:
            self.id = str(uuid4())
        if rack is None:
            rack = []
        self.rack = rack
