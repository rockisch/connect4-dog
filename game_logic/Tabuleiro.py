from enum import Enum
from dataclasses import dataclass


MAX_X = 7
MAX_Y = 6


class SlotState(Enum):
    EMPTY = 0
    P1 = 1
    P2 = 2


@dataclass
class Tabuleiro:
    def __init__(self) -> None:
        super().__init__()

    def is_column_available(self, y: int) -> bool:
        return (y % 2) > 0

    def get_position(self, x, y):
        return SlotState.EMPTY if x % 2 else SlotState.P1 if y % 2 else SlotState.P2
