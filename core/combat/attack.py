from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Collection, Type, Iterable, Optional

from core.traits import Trait
if TYPE_CHECKING:
    from core.creature import Creature
    from core.constants import MeleeRange, AttackForce, PrimaryAttribute
    from core.dice import DicePool, dice
    from core.combat.damage import DamageType
    from core.combat.criticals import CriticalEffect
    from core.contest import CombatSkillClass, CombatTest

class MeleeAttackTemplate:
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
                 skill_class: CombatSkillClass = None,
                 criticals: Iterable[Type[CriticalEffect]] = (),
                 traits: Iterable[AttackTrait] = ()):

        self.name = name
        self.max_reach = max(reach)
        self.min_reach = min(reach)
        self.force = force
        self.damtype = damtype
        self.damage = damage
        self.armpen = armpen
        self.skill_class = skill_class
        self.criticals = tuple(criticals)
        self.traits = tuple(traits)

    @property
    def combat_test(self) -> CombatTest:
        return self.skill_class.contest

    def can_reach(self, range: MeleeRange) -> bool:
        return self.min_reach <= range <= self.max_reach

    def can_defend(self) -> bool:
        if CannotDefendTrait in self.traits:
            return False
        return True

    def create_instance(self, attacker: Creature, use_hands: int) -> MeleeAttack:
        """Use this MeleeAttack as a template to create a new attack adjusted for the given attacker"""
        return MeleeAttack(self, attacker, use_hands)

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

class MeleeAttack:
    def __init__(self, template: MeleeAttackTemplate, attacker: Creature, use_hands: int):
        self.template = template
        self.attacker = attacker
        self.use_hands = use_hands

    def can_reach(self, range: MeleeRange) -> bool:
        return self.template.can_reach(range)

    def can_attack(self, range: MeleeRange) -> bool:
        return self.can_reach(range)

    def can_defend(self, range: MeleeRange) -> bool:
        return self.template.can_defend() and self.min_reach <= range

    @property
    def name(self) -> str:
        return self.template.name

    @property
    def skill_class(self) -> CombatSkillClass:
        return self.template.skill_class

    @property
    def combat_test(self) -> CombatTest:
        return self.template.combat_test

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

        # not sure if this makes two-handed weapons too strong
        # maybe make it just excesss hands? (e.g. using 1-handed weapon in two hands)
        return int(str_mod * 1.5) if self.use_hands > 1 else str_mod

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
        # noinspection PyTypeChecker
        if self.armpen.max() > 0:
            return f'[{self.damage}/{self.armpen}*]{self.damtype.format_type_code()}'
        return f'[{self.damage}]{self.damtype.format_type_code()}'

class AttackTrait(Trait):
    pass

class CannotDefendTrait(AttackTrait):
    name = 'Cannot Parry'
    desc = 'This attack cannot be used to parry in defence.'
CannotDefendTrait = CannotDefendTrait()