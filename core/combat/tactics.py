from typing import TYPE_CHECKING, Iterable, Mapping

from core.constants import MeleeRange
from core.contest import SkillLevel
from core.combat.attack import MeleeAttackInstance
if TYPE_CHECKING:
    from core.creature import Creature

# relative mean calculated using anydice.com
SKILL_FACTOR = {
    SkillLevel(0) : 0.78, # none
    SkillLevel(1) : 1.00, # competent
    SkillLevel(2) : 1.18, # proficient
    SkillLevel(3) : 1.33, # talented
    SkillLevel(4) : 1.46, # expert
    SkillLevel(5) : 1.58, # master
}

def get_attack_priority(attacker: 'Creature',
                        target: 'Creature',
                        attacks: Iterable[MeleeAttackInstance] = None) -> Mapping[MeleeAttackInstance, float]:
    return {
        attack : get_expected_damage(attack, target) * SKILL_FACTOR[attacker.get_skill_level(attack.skill_class.contest)]
        for attack in attacks or attacker.get_melee_attacks()
    }

def get_attack_priority_at_range(attacker: 'Creature',
                                 target: 'Creature',
                                 reach: MeleeRange,
                                 attacks: Iterable[MeleeAttackInstance] = None) -> Mapping[MeleeAttackInstance, float]:
    return {
        attack : get_expected_damage(attack, target) * SKILL_FACTOR[attacker.get_skill_level(attack.skill_class.contest)]
        for attack in attacks or attacker.get_melee_attacks()
        if attack.can_reach(reach)
    }

def get_expected_damage(attack: MeleeAttackInstance, target: 'Creature') -> float:
    result = 0
    for bp_id in target.bodyplan.get_bodypart_ids():
        result += target.bodyplan.get_relative_size(bp_id) * get_expected_damage_part(attack, target, bp_id)
    return result

def get_expected_damage_part(attack: MeleeAttackInstance, target: 'Creature', bp_id: str) -> float:
    damage, armpen = attack.damage.mean(), attack.armpen.mean()
    armor = target.get_armor(bp_id)
    return max(0.0, damage - armor, min(armpen, damage))

def get_melee_range_priority(creature: 'Creature', opponent: 'Creature', *, caution: float = 1.0) -> Mapping[MeleeRange, float]:
    range_priority = {}
    for i in range(creature.get_melee_engage_distance() + 1):
        reach = MeleeRange(i)
        attack_priority = get_attack_priority_at_range(creature, opponent, reach)
        power = max(attack_priority.values(), default=0.0)

        threat_priority = get_attack_priority_at_range(opponent, creature, reach)
        threat = max(threat_priority.values(), default=0.0)
        danger = (2*caution*threat + creature.health)/creature.health

        range_priority[reach] = power/danger
    return range_priority

