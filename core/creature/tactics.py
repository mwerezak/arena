from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Mapping, Optional, Tuple

from core.constants import MeleeRange
from core.combat.melee import get_defence_damage_mult
from core.contest import SkillLevel, Contest, SKILL_EVADE

if TYPE_CHECKING:
    from core.creature import Creature
    from core.creature.combat import ChangeMeleeRangeAction, MeleeCombat
    from core.combat.attack import MeleeAttackInstance
    from core.contest import OpposedResult
    from core.equipment import Equipment
    from core.equipment.weapon import ShieldBlock

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
def get_melee_attack_priority(attacker: Creature, target: Creature, attacks: Iterable[MeleeAttackInstance]) -> Mapping[MeleeAttackInstance, float]:
    return {
        attack : get_expected_damage(attack, target) * SKILL_FACTOR[attacker.get_skill_level(attack.combat_test)] for attack in attacks
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
        attacks = (attack for attack in protagonist.get_melee_attacks() if attack.can_reach(reach))
        attack_priority = get_melee_attack_priority(protagonist, opponent, attacks)
        power = max(attack_priority.values(), default=0.0)

        attacks = (attack for attack in opponent.get_melee_attacks() if attack.can_reach(reach))
        threat_priority = get_melee_attack_priority(opponent, protagonist, attacks)
        threat = max(threat_priority.values(), default=0.0)
        danger = (2 * caution * threat + protagonist.health) / protagonist.health

        range_priority[reach] = power/danger
    return range_priority

def get_melee_threat_value(protagonist: Creature, opponent: Creature) -> float:
    threat_priority = get_melee_attack_priority(opponent, protagonist, opponent.get_melee_attacks())
    threat_value = max(threat_priority.values(), default=0.0)

    attack_priority = get_melee_attack_priority(protagonist, opponent, protagonist.get_melee_attacks())
    attack_value = max(attack_priority.values(), default=0.0)
    return threat_value * attack_value / opponent.health

class CombatTactics:
    def __init__(self, parent: Creature):
        self.parent = parent

    # TODO customizable variability
    def _choose_attack(self, attack_priority: Mapping[MeleeAttackInstance, float]) -> Optional[MeleeAttackInstance]:
        return max(attack_priority.keys(), key=lambda k: attack_priority[k], default=None)

    def get_normal_attack(self, target: Creature, range: MeleeRange) -> Optional[MeleeAttackInstance]:
        attacks = (attack for attack in self.parent.get_melee_attacks() if attack.can_attack(range))
        attack_priority = get_melee_attack_priority(self.parent, target, attacks=attacks)
        return self._choose_attack(attack_priority)

    def get_opportunity_attack(self, target: Creature, attack_ranges: Iterable[MeleeRange]) -> Optional[MeleeAttackInstance]:
        attacks = (attack for attack in self.parent.get_melee_attacks() if any(attack.can_attack(r) for r in attack_ranges))
        attack_priority = get_melee_attack_priority(self.parent, target, attacks)
        return self._choose_attack(attack_priority)

    def get_melee_defence(self, attacker: Creature, attack: MeleeAttackInstance, range: MeleeRange) -> Optional[MeleeAttackInstance]:
        defend_priority = {
            defence : (
                1.0 - get_defence_damage_mult(attack.force, defence.force),
                self.parent.get_skill_level(defence.combat_test).value
            )
            for defence in self.parent.get_melee_attacks() if defence.can_defend(range)
        }
        return max(defend_priority.keys(), key=lambda k: defend_priority[k], default=None)

    def get_melee_shield(self) -> Optional[Equipment]:
        block_priority = {
            item : ( item.shield.block_bonus, item.shield.block_force )
            for item in self.parent.get_held_shields()
        }
        return max(block_priority.keys(), key=lambda k: block_priority[k], default=None)



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
        if change_range.allow_opportunity_attack() and self._can_attack(change_range.get_opportunity_attack_ranges()):
            change_range_success_chance = Contest.get_opposed_chance(change_range.protagonist, SKILL_EVADE, self.parent)
            if change_range_success_chance > 0.667:
                return False

        return True

    def _can_attack(self, ranges: Iterable[MeleeRange]) -> bool:
        ranges = list(ranges)
        return any(any(attack.can_reach(r) for r in ranges) for attack in self.parent.get_melee_attacks())

    def choose_evade_attack(self, attacker: Creature, attack: MeleeAttackInstance) -> bool:
        return False # TODO