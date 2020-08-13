from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Mapping, Optional, Collection

from core.constants import MeleeRange
from core.contest import SkillLevel, Contest, SKILL_EVADE

if TYPE_CHECKING:
    from core.creature import Creature
    from core.combat.attack import MeleeAttackInstance
    from core.creature.combat import ChangeMeleeRangeAction

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
def get_melee_attack_priority(attacker: Creature, target: Creature,
                              reach: Optional[Iterable[MeleeRange]] = None,
                              attacks: Iterable[MeleeAttackInstance] = None) -> Mapping[MeleeAttackInstance, float]:

    return {
        attack : get_expected_damage(attack, target) * SKILL_FACTOR[attacker.get_skill_level(attack.skill_class.contest)]
        for attack in attacks or attacker.get_melee_attacks()
        if reach is None or any(attack.can_reach(r) for r in reach)
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
        attack_priority = get_melee_attack_priority(protagonist, opponent, [reach])
        power = max(attack_priority.values(), default=0.0)

        threat_priority = get_melee_attack_priority(opponent, protagonist, [reach])
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

class CombatTactics:
    def __init__(self, parent: Creature):
        self.parent = parent

    # TODO customizable variability
    def choose_attack(self, attack_priority: Mapping[MeleeAttackInstance, float]) -> Optional[MeleeAttackInstance]:
        return max(attack_priority.keys(), key=lambda k: attack_priority[k], default=None)

    def can_attack(self, ranges: Iterable[MeleeRange]) -> bool:
        ranges = list(ranges)
        return any(any(attack.can_reach(r) for r in ranges) for attack in self.parent.get_melee_attacks())

    def choose_contest_change_range(self, change_range: ChangeMeleeRangeAction) -> bool:
        """Return True if the creature will try to contest an opponent's range change, giving up their attack of opportunity"""
        melee = self.parent.get_melee_combat(change_range.protagonist)

        # if we are also changing range and the range change takes us closer to the desired range, do not contest
        cur_action = self.parent.get_current_action()
        if isinstance(cur_action, ChangeMeleeRangeAction):
            cur_distance = abs(cur_action.desired_range - melee.separation)
            new_distance = abs(cur_action.desired_range - change_range.desired_range)
            if new_distance < cur_distance:
                return False

        # if we can opportunity attack and the success chance for contesting
        # is small enough, do not give up our opportunity attack to contest
        if change_range.allow_opportunity_attack() and self.can_attack(change_range.get_opportunity_attack_ranges()):
            change_range_success_chance = Contest.get_opposed_chance(change_range.protagonist, SKILL_EVADE, self.parent)
            if change_range_success_chance > 0.667:
                return False

        return True

    def get_normal_attack(self, target: Creature, attack_range: MeleeRange) -> Optional[MeleeAttackInstance]:
        attack_priority = get_melee_attack_priority(self.parent, target, [attack_range])
        return self.choose_attack(attack_priority)

    def get_opportunity_attack(self, target: Creature, attack_ranges: Iterable[MeleeRange]) -> Optional[MeleeAttackInstance]:
        attack_priority = get_melee_attack_priority(self.parent, target, attack_ranges)
        return self.choose_attack(attack_priority)

    def get_melee_defence(self, attacker: Creature, attack: MeleeAttackInstance) -> Optional[MeleeAttackInstance]:
        pass