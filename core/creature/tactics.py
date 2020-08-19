from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Mapping, Optional

import random
from core.constants import MeleeRange
from core.combat.resolver import get_parry_damage_mult
from core.contest import SkillLevel, Contest, SKILL_EVADE
from core.combat.melee import ChangeMeleeRangeAction, can_interrupt_action

if TYPE_CHECKING:
    from core.creature import Creature
    from core.combat.attack import MeleeAttack
    from core.equipment import Equipment

# relative mean calculated using anydice.com
SKILL_FACTOR = {
    SkillLevel(0) : 0.78, # none
    SkillLevel(1) : 1.00, # competent
    SkillLevel(2) : 1.18, # proficient
    SkillLevel(3) : 1.33, # talented
    SkillLevel(4) : 1.46, # expert
    SkillLevel(5) : 1.58, # master
}

def get_expected_damage(attack: MeleeAttack, target: Creature) -> float:
    result = 0
    for bp in target.get_bodyparts():
        result += bp.exposure * bp.get_effective_damage(attack.damage.mean(), attack.armpen.mean())
    return result

def get_melee_attack_value(attack: MeleeAttack, attacker: Creature, target: Creature) -> float:
    expected_damage = get_expected_damage(attack, target)
    skill_factor = SKILL_FACTOR[attacker.get_skill_level(attack.combat_test)]
    return expected_damage * skill_factor

# include only weapons that can attack at or within the given ranges
def get_melee_attack_priority(attacker: Creature, target: Creature, attacks: Iterable[MeleeAttack]) -> Mapping[MeleeAttack, float]:
    return {attack : get_melee_attack_value(attack, attacker, target) for attack in attacks}

def choose_attack(attack_priority: Mapping[MeleeAttack, float]) -> Optional[MeleeAttack]:
    best_value = max(attack_priority.values(), default=None)
    if best_value is None:
        return None
    top = { attack : value**3 for attack, value in attack_priority.items() if value > 0.75*best_value }
    if len(top) > 0:
        result = random.choices(*zip(*top.items()))
        return result[0]
    return None

class CombatTactics:
    def __init__(self, parent: Creature):
        self.parent = parent

    def get_normal_attack(self, target: Creature, reach: MeleeRange) -> Optional[MeleeAttack]:
        attacks = (attack for attack in self.parent.get_melee_attacks() if attack.can_attack(reach))
        attack_priority = get_melee_attack_priority(self.parent, target, attacks)
        return choose_attack(attack_priority)

    def get_secondary_attack(self, target: Creature, reach: MeleeRange, secondary: Iterable[MeleeAttack]) -> Optional[MeleeAttack]:
        attacks = (attack for attack in secondary if attack.can_attack(reach))
        attack_priority = get_melee_attack_priority(self.parent, target, attacks)
        return choose_attack(attack_priority)

    def get_opportunity_attack(self, target: Creature, attack_ranges: Iterable[MeleeRange]) -> Optional[MeleeAttack]:
        attack_ranges = list(attack_ranges)
        attacks = (attack for attack in self.parent.get_melee_attacks() if any(attack.can_attack(r) for r in attack_ranges))
        attack_priority = get_melee_attack_priority(self.parent, target, attacks)
        return choose_attack(attack_priority)

    def get_melee_defence(self, attacker: Creature, attack: MeleeAttack, reach: MeleeRange) -> Optional[MeleeAttack]:
        defend_priority = {}
        for defence in self.parent.get_melee_attacks():
            if defence.can_defend(reach):
                skill_level = self.parent.get_skill_level(defence.combat_test).value
                block_effectiveness = 1.0 - get_parry_damage_mult(attack.force, defence.force)
                defend_priority[defence] = (skill_level, block_effectiveness, defence.force, random.random())
        return max(defend_priority.keys(), key=lambda k: defend_priority[k], default=None)

    def get_melee_shield(self, range: MeleeRange) -> Optional[Equipment]:
        block_priority = {
            item : ( item.shield.block_bonus, item.shield.block_force )
            for item in self.parent.get_held_shields() if item.shield.can_block(range)
        }
        return max(block_priority.keys(), key=lambda k: block_priority[k], default=None)

    def get_range_change_desire(self, opponent: Creature, from_range: MeleeRange, to_range: MeleeRange) -> float:
        """-1.0 to 1.0 scale rating how favorable the given range change is"""
        range_scores = self.get_melee_range_priority(opponent)
        from_score = range_scores.get(from_range, 0)
        to_score = range_scores.get(to_range, 0)
        if from_score == 0:
            return 1.0

        modifier = ChangeMeleeRangeAction.get_contest_modifier(self.parent) - ChangeMeleeRangeAction.get_contest_modifier(opponent)
        success_chance = Contest.get_opposed_chance(self.parent, SKILL_EVADE, opponent, SKILL_EVADE, modifier.contest)
        return min(max(-1.0, (to_score/from_score - 1.0)/0.25 * success_chance), 1.0)

    def choose_change_range_response(self, change_range: ChangeMeleeRangeAction) -> Optional[str]:
        """Return True if the creature will try to contest an opponent's range change, giving up their attack of opportunity"""

        melee = self.parent.get_melee_combat(change_range.protagonist)
        change_score = self.get_range_change_desire(change_range.protagonist, melee.get_separation(), change_range.target_range)
        opponent_success = Contest.get_opposed_chance(change_range.protagonist, SKILL_EVADE, self.parent)

        if change_score >= 0:
            return None

        can_opportunity_attack = (
            can_interrupt_action(self.parent)
            and change_range.allow_opportunity_attack()
            and self._can_attack(change_range.get_opportunity_attack_ranges())
        )
        threshold = min(-change_score, 2/3)
        if can_opportunity_attack and opponent_success > threshold:
            return 'attack'
        return 'contest'

    def _can_attack(self, ranges: Iterable[MeleeRange]) -> bool:
        ranges = list(ranges)
        return any(any(attack.can_attack(r) for r in ranges) for attack in self.parent.get_melee_attacks())

    def get_melee_range_priority(self, opponent: Creature, *, caution: float = 1.0) -> Mapping[MeleeRange, float]:
        range_priority = {}
        melee = self.parent.get_melee_combat(opponent)
        for reach in MeleeRange.range(melee.get_min_separation(), self.parent.get_melee_engage_distance() + 1):
            pro_attacks = (attack for attack in self.parent.get_melee_attacks() if attack.can_attack(reach))
            attack_priority = get_melee_attack_priority(self.parent, opponent, pro_attacks)
            power = max(attack_priority.values(), default=0.0)

            ant_attacks = (attack for attack in opponent.get_melee_attacks() if attack.can_attack(reach))
            threat_priority = get_melee_attack_priority(opponent, self.parent, ant_attacks)
            threat = max(threat_priority.values(), default=0.0)

            health = self.parent.health + self.parent.max_health
            danger = (2 * caution * threat + health) / health

            range_priority[reach] = power/danger
        return range_priority

    def get_desired_melee_range(self, opponent: Creature, *, caution: float = 1.0) -> Optional[MeleeRange]:
        melee = self.parent.get_melee_combat(opponent)
        range_priority = self.get_melee_range_priority(opponent, caution=caution)

        # tiebreakers: if range is equal to current range, then greatest range
        return max(range_priority.keys(), key=lambda k: (round(range_priority[k],2), int(k==melee.get_separation()), k), default=None)

    def get_melee_threat_value(self, opponent: Creature) -> float:
        threat_priority = get_melee_attack_priority(opponent, self.parent, opponent.get_melee_attacks())
        threat_value = max(threat_priority.values(), default=0.0)

        attack_priority = get_melee_attack_priority(self.parent, opponent, self.parent.get_melee_attacks())
        attack_value = max(attack_priority.values(), default=0.0)
        return threat_value * attack_value / (opponent.health + opponent.max_health)

    def get_weapon_value(self, item: Equipment, opponent: Creature, reach: Optional[MeleeRange] = None) -> float:
        return max((
            get_melee_attack_value(attack, self.parent, opponent)
            for attack in item.get_melee_attacks(self.parent)
            if reach is None or attack.can_attack(reach)
        ), default=0)

    def get_weapon_change_desire(self, from_item: Equipment, to_item: Equipment, opponent: Creature, reach: Optional[MeleeRange] = None) -> float:
        from_value = self.get_weapon_value(from_item, opponent, reach)
        to_value = self.get_weapon_value(to_item, opponent, reach)
        return self.get_switch_attack_desire(from_value, to_value)

    @staticmethod
    def get_switch_attack_desire(from_value: float, to_value: float) -> float:
        if from_value == 0:
            return 1.0
        return min(max(-1.0, (to_value/from_value - 1.0)/2.0), 1.0)