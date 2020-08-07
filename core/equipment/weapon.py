from copy import copy as shallow_copy
from typing import Iterable, Optional, NamedTuple

from core.equipment import Equipment
from core.combat.attack import MeleeAttack
from core.constants import AttackForce, SizeCategory

class Weapon(Equipment):
    def __init__(self,
                 name: str,
                 size: SizeCategory,
                 encumbrance: float,
                 cost: float,
                 melee: Iterable[MeleeAttack] = None,
                 shield: Optional['ShieldBlock'] = None):
        self.name = name
        self.size = size
        self.encumbrance = encumbrance
        self.cost = cost
        self.melee = list(melee) if melee is not None else []
        self.shield = shield

    def is_melee_weapon(self) -> bool:
        return len(self.melee) > 0

    def is_shield(self) -> bool:
        return self.shield is not None

    def clone(self, name: str = None) -> 'Weapon':
        result = shallow_copy(self)
        if name is not None:
            result.name = name
        return result

class ShieldBlock(NamedTuple):
    block_force: AttackForce
    block_bonus: int
    block_ranged: float


"""
_DICE_UPGRADE_TABLE = [
    [ (1,3),  (1,4)],
    [ (1,4),  (1,6)],
    [ (1,6),  (1,8)],
    [ (1,8), (1,12)],
    [ (2,4),  (2,6)],
    [(1,10),  (2,8)],
]
"""
