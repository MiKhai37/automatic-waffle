from uuid import uuid4
from .tile import Tile


class Player:
    def __init__(self, player_id: str = None, score: int = None, rack: list[Tile] = None) -> None:
        self.player_id = player_id if player_id is not None else str(uuid4())
        self.rack = rack if rack is not None else []
        self.score = score if score is not None else 0

    def __repr__(self) -> str:
        return f'Player: {self.player_id}, {self.score}, {self.rack}'