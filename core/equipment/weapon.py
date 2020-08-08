from copy import copy as shallow_copy
from typing import Iterable, Optional, NamedTuple

from core.equipment import Equipment
from core.combat.attack import MeleeAttack
from core.constants import AttackForce, SizeCategory
from core.contest import CombatSkillClass

class Weapon(Equipment):
    def __init__(self,
                 name: str,
                 size: SizeCategory,
                 skill_class: CombatSkillClass,
                 encumbrance: float,
                 cost: float,
                 melee_attacks: Iterable[MeleeAttack] = (),
                 shield: Optional['ShieldBlock'] = None):

        self.name = name
        self.size = size
        self.skill_class = skill_class
        self.encumbrance = encumbrance
        self.cost = cost
        self.shield = shield

        self.melee_attacks = list(melee_attacks)
        for attack in melee_attacks:
            if attack.skill_class is None:
                attack.skill_class = self.skill_class

    def is_melee_weapon(self) -> bool:
        return len(self.melee_attacks) > 0

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


DICE_UPGRADE_TABLE = [
    [ (1,3),  (1,4)],
    [ (1,4),  (1,6)],
    [ (1,6),  (1,8)],
    [ (1,8), (1,12)],
    [ (2,4),  (2,6)],
    [(1,10),  (2,8)],
]
