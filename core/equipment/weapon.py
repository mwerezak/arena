from copy import copy as shallow_copy
from typing import TYPE_CHECKING, Iterable, Optional, NamedTuple, Tuple

from core.equipment import Equipment
from core.combat.attack import MeleeAttack
from core.constants import AttackForce, SizeCategory
from core.contest import CombatSkillClass
if TYPE_CHECKING:
    from core.creature import Creature

class Weapon(Equipment):
    def __init__(self,
                 name: str,
                 size: SizeCategory,
                 skill_class: CombatSkillClass,
                 encumbrance: float,
                 cost: int,
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

    def get_melee_attacks(self) -> Iterable[MeleeAttack]:
        return iter(self.melee_attacks)

    def get_required_grip(self, creature: 'Creature') -> Optional[Tuple[int, int]]:
        creature_size = creature.size.get_category()
        if self.size > creature_size.get_step(1):
            return None
        if self.size > creature_size:
            return 2,2
        return 1,2

    def is_light_weapon(self, creature: 'Creature') -> bool:
        return self.size < creature.size.get_category()

    def clone(self, name: str = None) -> 'Weapon':
        result = shallow_copy(self)
        if name is not None:
            result.name = name
        return result

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'

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
