from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Mapping, Optional, Any

from core.constants import MeleeRange
from core.combat.resolver import get_parry_damage_mult
from core.contest import SkillLevel, Contest, SKILL_EVADE
from core.creature.combat import ChangeMeleeRangeAction

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

# include only weapons that can attack at or within the given ranges
def get_melee_attack_priority(attacker: Creature, target: Creature, attacks: Iterable[MeleeAttack]) -> Mapping[MeleeAttack, float]:
    result = {}
    for attack in attacks:
        expected_damage = get_expected_damage(attack, target)
        skill_factor = SKILL_FACTOR[attacker.get_skill_level(attack.combat_test)]
        result[attack] = expected_damage * skill_factor
    return result

def get_expected_damage(attack: MeleeAttack, target: Creature) -> float:
    result = 0
    for bp in target.get_bodyparts():
        result += bp.exposure * bp.get_effective_damage(attack.damage.mean(), attack.armpen.mean())
    return result

class CombatTactics:
    def __init__(self, parent: Creature):
        self.parent = parent

    # TODO customizable variability
    def _choose_attack(self, attack_priority: Mapping[MeleeAttack, float]) -> Optional[MeleeAttack]:
        return max(attack_priority.keys(), key=lambda k: (attack_priority[k], k.force), default=None)

    def get_normal_attack(self, target: Creature, range: MeleeRange) -> Optional[MeleeAttack]:
        attacks = (attack for attack in self.parent.get_melee_attacks() if attack.can_attack(range))
        attack_priority = get_melee_attack_priority(self.parent, target, attacks)
        return self._choose_attack(attack_priority)

    def get_secondary_attack(self, target: Creature, range: MeleeRange, secondary: Iterable[MeleeAttack]) -> Optional[MeleeAttack]:
        attacks = (attack for attack in secondary if attack.can_attack(range))
        attack_priority = get_melee_attack_priority(self.parent, target, attacks)
        return self._choose_attack(attack_priority)

    def get_opportunity_attack(self, target: Creature, attack_ranges: Iterable[MeleeRange]) -> Optional[MeleeAttack]:
        attack_ranges = list(attack_ranges)
        attacks = (attack for attack in self.parent.get_melee_attacks() if any(attack.can_attack(r) for r in attack_ranges))
        attack_priority = get_melee_attack_priority(self.parent, target, attacks)
        return self._choose_attack(attack_priority)

    def get_melee_defence(self, attacker: Creature, attack: MeleeAttack, range: MeleeRange) -> Optional[MeleeAttack]:
        defend_priority = {}
        for defence in self.parent.get_melee_attacks():
            if defence.can_defend(range):
                skill_level = self.parent.get_skill_level(defence.combat_test).value
                block_effectiveness = 1.0 - get_parry_damage_mult(attack.force, defence.force)
                defend_priority[defence] = (skill_level, block_effectiveness, defence.force)
        return max(defend_priority.keys(), key=lambda k: defend_priority[k], default=None)

    def get_melee_shield(self, range: MeleeRange) -> Optional[Equipment]:
        block_priority = {
            item : ( item.shield.block_bonus, item.shield.block_force )
            for item in self.parent.get_held_shields() if item.shield.can_block(range)
        }
        return max(block_priority.keys(), key=lambda k: block_priority[k], default=None)

    def get_range_change_desire(self, opponent: Creature, from_range: MeleeRange, to_range: MeleeRange) -> Optional[float]:
        """-1.0 to 1.0 scale rating how favorable the given range change is"""
        range_scores = self.get_melee_range_priority(opponent)
        from_score = range_scores.get(from_range, 0)
        to_score = range_scores.get(to_range, 0)
        if from_score == 0:
            return None
        return min(max(-1.0, (to_score/from_score - 1.0)/0.25), 1.0)

    def choose_contest_change_range(self, change_range: ChangeMeleeRangeAction) -> Optional[str]:
        """Return True if the creature will try to contest an opponent's range change, giving up their attack of opportunity"""

        melee = self.parent.get_melee_combat(change_range.protagonist)
        change_score = self.get_range_change_desire(change_range.protagonist, melee.separation, change_range.target_range)
        opponent_success = Contest.get_opposed_chance(change_range.protagonist, SKILL_EVADE, self.parent)

        if change_score is None:
            contest = True
        elif change_score >= 0:
            contest = False
        else:
            contest = -max(change_score, 2/3) <= opponent_success

        if contest:
            can_opportunity_attack = change_range.allow_opportunity_attack() and self._can_attack(change_range.get_opportunity_attack_ranges())
            threshold = -max(change_score, 2/3) if change_score is not None else 2/3
            if can_opportunity_attack and opponent_success > threshold:
                return 'attack'
            return 'contest'
        return None

    def _can_attack(self, ranges: Iterable[MeleeRange]) -> bool:
        ranges = list(ranges)
        return any(any(attack.can_attack(r) for r in ranges) for attack in self.parent.get_melee_attacks())

    def choose_evade_attack(self, attacker: Creature, attack: MeleeAttack) -> bool:
        return False # TODO

    def get_melee_range_priority(self, opponent: Creature, *, caution: float = 1.0) -> Mapping[MeleeRange, float]:
        range_priority = {}
        for reach in MeleeRange.range(self.parent.get_melee_engage_distance() + 1):
            attacks = (attack for attack in self.parent.get_melee_attacks() if attack.can_reach(reach))
            attack_priority = get_melee_attack_priority(self.parent, opponent, attacks)
            power = max(attack_priority.values(), default=0.0)

            attacks = (attack for attack in opponent.get_melee_attacks() if attack.can_reach(reach))
            threat_priority = get_melee_attack_priority(opponent, self.parent, attacks)
            threat = max(threat_priority.values(), default=0.0)
            danger = (2 * caution * threat + self.parent.health) / self.parent.health

            range_priority[reach] = power/danger
        return range_priority

    def get_desired_melee_range(self, opponent: Creature, *, caution: float = 1.0) -> Optional[MeleeRange]:
        melee = self.parent.get_melee_combat(opponent)
        range_priority = self.get_melee_range_priority(opponent, caution=caution)

        # tiebreakers: if range is equal to current range, then greatest range
        return max(range_priority.keys(), key=lambda k: (range_priority[k], int(k==melee.separation), k), default=None)

    def get_melee_threat_value(self, opponent: Creature) -> float:
        threat_priority = get_melee_attack_priority(opponent, self.parent, opponent.get_melee_attacks())
        threat_value = max(threat_priority.values(), default=0.0)

        attack_priority = get_melee_attack_priority(self.parent, opponent, self.parent.get_melee_attacks())
        attack_value = max(attack_priority.values(), default=0.0)
        return threat_value * attack_value / opponent.health