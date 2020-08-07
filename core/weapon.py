from copy import copy as shallow_copy
from typing import Iterable

from core.equipment import Equipment
from core.melee.attack import MeleeAttack
from core.creature import SizeCategory

class Weapon(Equipment):
    def __init__(self,
                 name: str,
                 size: SizeCategory,
                 encumbrance: float,
                 cost: float,
                 melee: Iterable[MeleeAttack] = None,
                 shield: int = 0):
        self.name = name
        self.size = size
        self.encumbrance = encumbrance
        self.cost = cost
        self.melee = list(melee) if melee is not None else []
        self.shield = shield

    def is_melee_weapon(self) -> bool:
        return len(self.melee) > 0

    def is_shield(self) -> bool:
        return self.shield > 0

    def clone(self, name: str = None) -> 'Weapon':
        result = shallow_copy(self)
        if name is not None:
            result.name = name
        return result