from typing import Protocol

class Equipment(Protocol):
    name: str
    cost: float
    encumbrance: float  # encumbrance when worn or equipped
