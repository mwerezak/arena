from __future__ import annotations

from copy import copy as shallow_copy
from typing import TYPE_CHECKING, Iterable, Optional, NamedTuple, Tuple

from core.equipment.template import EquipmentTemplate

if TYPE_CHECKING:
    from core.creature import Creature
    from core.combat.attack import MeleeAttackTemplate, MeleeAttack
    from core.constants import AttackForce, SizeCategory
    from core.contest import CombatSkillClass, CombatTest

class ShieldBlock(NamedTuple):
    block_force: AttackForce
    block_bonus: int
    block_ranged: float

class Weapon(EquipmentTemplate):
    def __init__(self,
                 name: str,
                 size: SizeCategory,
                 skill_class: CombatSkillClass,
                 encumbrance: float,
                 cost: int,
                 melee_attacks: Iterable[MeleeAttackTemplate] = (),
                 shield: Optional[ShieldBlock] = None):

        self.name = name
        self.size = size
        self.skill_class = skill_class
        self.encumbrance = encumbrance
        self.cost = cost
        self.block = shield

        self.melee_attacks = list(melee_attacks)
        for attack in melee_attacks:
            attack.name = f'{self.name} ({attack.name})'
            if attack.skill_class is None:
                attack.skill_class = self.skill_class

    def is_melee_weapon(self) -> bool:
        return len(self.melee_attacks) > 0

    def is_shield(self) -> bool:
        return self.block is not None

    def get_melee_attacks(self, attacker: Creature, use_hands: int = 0) -> Iterable[MeleeAttack]:
        for attack in self.melee_attacks:
            yield attack.create_instance(attacker, use_hands)

    def get_required_hands(self, creature: Creature) -> Optional[Tuple[int, int]]:
        """Return None if the equipment cannot be held, otherwise return the (minimum, maximum) number of hands needed to equip."""
        creature_size = creature.size.get_category()
        if self.size > creature_size.get_step(1):
            return None

        min_hands, max_hands = 1,2
        if self.is_large_weapon(creature):
            min_hands = 2
        elif self.is_light_weapon(creature) or self.is_shield():
            max_hands = 1
        return min_hands, max_hands

    def is_large_weapon(self, creature: Creature) -> bool:
        return self.size > creature.size.get_category()

    def is_light_weapon(self, creature: Creature) -> bool:
        return self.size < creature.size.get_category()

    @property
    def combat_test(self) -> CombatTest:
        return self.skill_class.contest

    def clone(self, name: str = None) -> Weapon:
        result = shallow_copy(self)
        if name is not None:
            result.name = name
        return result

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'

    def __str__(self) -> str:
        return self.name

# DICE_UPGRADE_TABLE = [
#     [ (1,3),  (1,4)],
#     [ (1,4),  (1,6)],
#     [ (1,6),  (1,8)],
#     [ (1,8), (1,12)],
#     [ (2,4),  (2,6)],
#     [(1,10),  (2,8)],
# ]
