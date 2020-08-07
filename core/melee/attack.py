from copy import copy as shallow_copy
from typing import TYPE_CHECKING, Tuple, Collection, Type, Iterable, Optional

from core.constants import MeleeRange, AttackForce
from core.dice import DicePool
from core.critical import CriticalEffect

if TYPE_CHECKING:
    from core.combat import DamageType


## MeleeAttacks

class MeleeAttack:
    name: str
    force: AttackForce
    damtype: 'DamageType'
    damage: DicePool
    criticals: Collection[Type[CriticalEffect]]

    def __init__(self,
                 name: str,
                 reach: Tuple[MeleeRange, MeleeRange],
                 force: AttackForce,
                 damtype: 'DamageType',
                 damage: DicePool,
                 armor_pen: Optional[DicePool] = None,
                 criticals: Iterable[Type[CriticalEffect]] = None):
        self.name = name
        self.max_reach = max(reach)
        self.min_reach = min(reach)
        self.force = force
        self.damtype = damtype
        self.damage = damage
        self.armor_pen = armor_pen
        self.criticals = tuple(criticals) if criticals is not None else ()

    def clone(self) -> 'MeleeAttack':
        return shallow_copy(self)