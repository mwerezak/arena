from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Mapping, Tuple

from core.constants import MeleeRange
from core.contest import SkillLevel

if TYPE_CHECKING:
    from core.creature import Creature
    from core.combat.attack import MeleeAttackInstance

# relative mean calculated using anydice.com
SKILL_FACTOR = {
    SkillLevel(0) : 0.78, # none
    SkillLevel(1) : 1.00, # competent
    SkillLevel(2) : 1.18, # proficient
    SkillLevel(3) : 1.33, # talented
    SkillLevel(4) : 1.46, # expert
    SkillLevel(5) : 1.58, # master
}

def get_melee_attack_priority(attacker: Creature, target: Creature,
                              attacks: Iterable[MeleeAttackInstance] = None) -> Mapping[MeleeAttackInstance, float]:
    return {
        attack : get_expected_damage(attack, target) * SKILL_FACTOR[attacker.get_skill_level(attack.skill_class.contest)]
        for attack in attacks or attacker.get_melee_attacks()
    }

# include only weapons that can attack at the given range
def get_melee_attack_priority_at_range(attacker: Creature, target: Creature, reach: MeleeRange,
                                       attacks: Iterable[MeleeAttackInstance] = None) -> Mapping[MeleeAttackInstance, float]:
    return {
        attack : get_expected_damage(attack, target) * SKILL_FACTOR[attacker.get_skill_level(attack.skill_class.contest)]
        for attack in attacks or attacker.get_melee_attacks()
        if attack.can_reach(reach)
    }

# include only weapons that can attack at or within the given ranges
def get_melee_attack_priority_at_ranges(attacker: Creature, target: Creature, reach: Tuple[MeleeRange, MeleeRange],
                                        attacks: Iterable[MeleeAttackInstance] = None) -> Mapping[MeleeAttackInstance, float]:

    min_range, max_range = min(reach), max(reach)
    ranges = list(MeleeRange.range(min_range, max_range+1))
    return {
        attack : get_expected_damage(attack, target) * SKILL_FACTOR[attacker.get_skill_level(attack.skill_class.contest)]
        for attack in attacks or attacker.get_melee_attacks()
        if any(attack.can_reach(r) for r in ranges)
    }

def get_expected_damage(attack: MeleeAttackInstance, target: Creature) -> float:
    result = 0
    for bp_id in target.bodyplan.get_bodypart_ids():
        result += target.bodyplan.get_relative_size(bp_id) * get_expected_damage_part(attack, target, bp_id)
    return result

def get_expected_damage_part(attack: MeleeAttackInstance, target: Creature, bp_id: str) -> float:
    damage, armpen = attack.damage.mean(), attack.armpen.mean()
    armor = target.get_armor(bp_id)
    return max(0.0, damage - armor, min(armpen, damage))

def get_melee_range_priority(protagonist: Creature, opponent: Creature, *, caution: float = 1.0) -> Mapping[MeleeRange, float]:
    range_priority = {}
    for reach in MeleeRange.range(protagonist.get_melee_engage_distance() + 1):
        attack_priority = get_melee_attack_priority_at_range(protagonist, opponent, reach)
        power = max(attack_priority.values(), default=0.0)

        threat_priority = get_melee_attack_priority_at_range(opponent, protagonist, reach)
        threat = max(threat_priority.values(), default=0.0)
        danger = (2 * caution * threat + protagonist.health) / protagonist.health

        range_priority[reach] = power/danger
    return range_priority

def get_melee_threat_value(protagonist: Creature, opponent: Creature) -> float:
    threat_priority = get_melee_attack_priority(opponent, protagonist)
    threat_value = max(threat_priority.values(), default=0.0)

    attack_priority = get_melee_attack_priority(protagonist, opponent)
    attack_value = max(attack_priority.values(), default=0.0)
    return threat_value * attack_value / opponent.health
