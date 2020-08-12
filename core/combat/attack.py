from copy import copy as shallow_copy
from typing import TYPE_CHECKING, Tuple, Collection, Type, Iterable, Optional

from core.constants import MeleeRange, AttackForce, PrimaryAttribute
from core.dice import DicePool, dice
from core.combat.damage import DamageType
from core.combat.criticals import CriticalEffect
from core.contest import CombatSkillClass

if TYPE_CHECKING:
    from core.creature import Creature

## MeleeAttacks

class MeleeAttack:
    name: str
    force: AttackForce
    damtype: DamageType
    damage: DicePool
    criticals: Collection[Type[CriticalEffect]]

    def __init__(self,
                 name: str,
                 reach: Tuple[MeleeRange, MeleeRange],
                 force: AttackForce,
                 damtype: DamageType,
                 damage: DicePool,
                 armpen: Optional[DicePool] = None,
                 criticals: Iterable[Type[CriticalEffect]] = (),
                 skill_class: CombatSkillClass = None):

        self.name = name
        self.max_reach = max(reach)
        self.min_reach = min(reach)
        self.force = force
        self.damtype = damtype
        self.damage = damage
        self.armpen = armpen
        self.criticals = tuple(criticals)
        self.skill_class = skill_class

    def can_reach(self, range: MeleeRange) -> bool:
        return self.min_reach <= range <= self.max_reach

    def create_instance(self, attacker: 'Creature', use_hands: int) -> 'MeleeAttackInstance':
        """Use this MeleeAttack as a template to create a new attack adjusted for the given attacker"""
        return MeleeAttackInstance(self, attacker, use_hands)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'

    def __str__(self) -> str:
        return f'{self.name}: ({self.format_reach()}) {self.force} {self.format_damage()}'

    def format_reach(self) -> str:
        if self.max_reach != self.min_reach:
            return str(self.max_reach) + ' - ' + str(self.min_reach)
        return str(self.max_reach)

    def format_damage(self) -> str:
        if self.armpen is not None:
            return f'[{self.damage}/{self.armpen}*]{self.damtype.format_type_code()}'
        return f'[{self.damage}]{self.damtype.format_type_code()}'

class MeleeAttackInstance:
    def __init__(self, template: MeleeAttack, attacker: 'Creature', use_hands: int):
        self.template = template
        self.attacker = attacker
        self.use_hands = use_hands

    def can_reach(self, range: MeleeRange) -> bool:
        return self.template.can_reach(range)

    @property
    def name(self) -> str:
        return self.template.name

    @property
    def skill_class(self) -> CombatSkillClass:
        return self.template.skill_class

    @property
    def max_reach(self) -> MeleeRange:
        return self.template.max_reach

    @property
    def min_reach(self) -> MeleeRange:
        return self.template.min_reach

    @property
    def str_modifier(self) -> int:
        if self.use_hands < 1:
            return 0
        str_mod = self.attacker.get_attribute(PrimaryAttribute.STR)
        if self.use_hands == 1:
            return str_mod
        return int(str_mod * 1.5)

    @property
    def force(self) -> AttackForce:
        return self.template.force

    @property
    def damtype(self) -> DamageType:
        return self.template.damtype

    @property
    def damage(self) -> DicePool:
        return self.template.damage + self.str_modifier

    @property
    def armpen(self) -> DicePool:
        if self.template.armpen is not None:
            return self.template.armpen + self.str_modifier
        return dice(0)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'

    def __str__(self) -> str:
        return f'{self.name}: ({self.format_reach()}) {self.force} {self.format_damage()}'

    def format_reach(self) -> str:
        if self.max_reach != self.min_reach:
            return str(self.max_reach) + ' - ' + str(self.min_reach)
        return str(self.max_reach)

    def format_damage(self) -> str:
        if self.armpen.max() > 0:
            return f'[{self.damage}/{self.armpen}*]{self.damtype.format_type_code()}'
        return f'[{self.damage}]{self.damtype.format_type_code()}'