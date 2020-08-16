from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Tuple
if TYPE_CHECKING:
    from core.creature import Creature

class EquipmentTemplate:
    name: str
    cost: int
    encumbrance: float = 0.0

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'

    def __str__(self) -> str:
        return self.name

    def get_required_hands(self, creature: Creature) -> Optional[Tuple[int, int]]:
        """Return None if the equipment cannot be held, otherwise return the (minimum, maximum) number of hands needed to equip."""
        return None