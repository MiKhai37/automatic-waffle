from uuid import uuid4
from .tile import Tile


class Player:
    def __init__(self, player_id: str = None, score: int = None, rack: list[Tile] = None) -> None:
        self.ID = player_id if player_id is not None else str(uuid4())
        self.rack = rack if rack is not None else []
        self.score = score if score is not None else 0

    def __repr__(self) -> str:
        return f'Player({self.ID}, {self.score}, {self.rack})'

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Player) and self.ID == __o.ID and self.rack == __o.rack and self.score == __o.score
