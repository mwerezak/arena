from typing import TYPE_CHECKING, Optional, Tuple
if TYPE_CHECKING:
    from core.creature import Creature

class Equipment:
    name: str
    cost: int

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'

    def get_required_grip(self, creature: 'Creature') -> Optional[Tuple[int, int]]:
        """Return None if the equipment cannot be held, otherwise return the (minimum, maximum) number of hands needed to equip."""
        return None