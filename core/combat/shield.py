from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple, Any

from core.combat.attack import get_natural_reach_bonus
from core.contest import SKILL_SHIELD, ContestModifier

if TYPE_CHECKING:
    from core.constants import MeleeRange, AttackForce
    from core.creature import Creature
    from core.contest import Contest


class ShieldTemplate(NamedTuple):
    min_reach: MeleeRange
    block_force: AttackForce
    block_bonus: int
    block_ranged: float
    combat_test: Contest = SKILL_SHIELD

    def create_instance(self, defender: Creature, source: Any) -> ShieldBlock:
        return ShieldBlock(self, defender, source)


class ShieldBlock:
    def __init__(self, template: ShieldTemplate, defender: Creature, source: Any):
        self.template = template
        self.defender = defender
        self.source = source

        reach_bonus = get_natural_reach_bonus(defender.size)
        self.min_reach = template.min_reach.get_step(reach_bonus)

    def can_block(self, range: MeleeRange):
        return range >= self.min_reach

    @property
    def force(self) -> AttackForce:
        return self.template.block_force

    @property
    def contest_modifier(self) -> ContestModifier:
        return ContestModifier(self.template.block_bonus)

    @property
    def block_ranged_chance(self):
        return self.template.block_ranged

    @property
    def combat_test(self) -> Contest:
        return self.template.combat_test