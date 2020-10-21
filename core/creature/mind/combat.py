from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional

from core.creature.bodypart import BodyPart
from core.creature.mind.tactics import CombatTactics, SKILL_FACTOR, get_melee_attack_value
from core.creature.actions import ChangeStanceAction, SwitchHeldItemAction
from core.equipment import Equipment
from core.combat.melee import ChangeMeleeRangeAction, MeleeCombatAction

if TYPE_CHECKING:
    from core.creature import Creature
    from core.creature.actions import CreatureAction
    from core.combat.attack import MeleeAttackTemplate

class CreatureMind(CombatTactics):
    def __init__(self, creature: Creature):
        self.creature = creature
        super(CreatureMind, self).__init__(creature)

    def next_combat_action(self) -> Optional[CreatureAction]:
        return get_next_action(self.creature)

def get_attack_value(creature: Creature, attack: MeleeAttackTemplate) -> float:
    return attack.damage.mean() * SKILL_FACTOR[creature.get_skill_level(attack.combat_test)]

def try_equip_best_weapons(creature: Creature) -> None:
    inventory = creature.inventory
    inventory.unequip_all()

    weapon_value = {}
    shield_value = {}
    for item in inventory:
        if item.is_weapon():
            weapon_value[item] = max((
                (attack.max_reach, get_attack_value(creature, attack)) for attack in item.get_melee_attacks(creature)
            ), default=(None, 0))[1]
            if item.is_shield():
                shield_value[item] = (item.shield.block_bonus, item.shield.block_force)

    # equip one weapon, then one shield, then the rest
    weapons = sorted(weapon_value.keys(), key=lambda k: weapon_value[k])
    best_shield = max(shield_value.keys(), key=lambda k: shield_value[k], default=None)

    item = weapons.pop()
    inventory.try_equip_item(item)
    if item == best_shield:
        best_shield = None

    if best_shield is not None:
        inventory.try_equip_item(best_shield)
        weapons.remove(best_shield)

    for item in reversed(weapons):
        if len(list(inventory.get_empty_slots())) == 0:
            break
        inventory.try_equip_item(item)

    ## if there are any left over hands, increase hand count of existing weapons
    for item in sorted(inventory.get_held_items(), key=lambda k: weapon_value[k], reverse=True):
        if len(list(inventory.get_empty_slots())) == 0:
            break
        _, max_hands = item.get_required_hands(creature)
        inventory.try_equip_item(item, use_hands=max_hands)


def get_next_action(protagonist: Creature) -> Optional[CreatureAction]:
    tactics = protagonist.mind

    if protagonist.stance < protagonist.max_stance:
        return ChangeStanceAction(protagonist.max_stance)

    opponents = { o : tactics.get_melee_threat_value(o) for o in protagonist.get_melee_opponents() }
    opponent = max(opponents, key=lambda k: opponents[k], default=None)
    if opponent is None:
        return None

    melee = protagonist.get_melee_combat(opponent)

    # change weapons?
    attack_values = (
        get_melee_attack_value(attack, protagonist, opponent)
        for attack in protagonist.get_melee_attacks()
        if attack.can_attack(melee.get_separation())
    )
    best_score = max(attack_values, default=0)
    equipped = [*protagonist.inventory.get_held_items()]
    available = (item for item in protagonist.inventory if item.is_weapon() and item not in equipped)
    available = {
        item : value for item in available
        if (value := protagonist.mind.get_weapon_value(item, opponent, melee.get_separation())) > 0
    }
    # unarmed attacks that are unavailable due to equipped weapons
    inv = protagonist.inventory
    occupied = [
        bp for bp in inv.get_equip_slots() if (item := inv.get_item_in_slot(bp)) is not None and not item.is_shield()
    ]
    for bp in occupied:
        if protagonist.inventory.get_item_in_slot(bp) is not None:
            value = max((
                get_melee_attack_value(attack, protagonist, opponent)
                for attack in bp.get_unarmed_attacks()
                if attack.can_attack(melee.get_separation())
            ), default=0)
            if value > 0:
                available[bp] = value

    # print(available)

    candidate = max(available.keys(), key=lambda k: available[k], default=None)
    if candidate is not None:
        candidate_score = available[candidate]

        if best_score > 0:
            change_desire = min(max(0.0, (candidate_score/best_score-1.0)/2.0), 1.0)
        else:
            change_desire = 1.0 if candidate_score > 0 else 0.0

        # print(f'{protagonist} weapon change desire: {change_desire:.2f}')
        if change_desire > 0 and random.random() < change_desire:
            change_weapon = True

            if isinstance(candidate, Equipment):
                min_hands, max_hands = candidate.get_required_hands(protagonist)

                unequip_candidates = sorted(
                    protagonist.inventory.get_held_items(),
                    key=lambda o: (
                        1 if o.is_shield() else 0,  # sort shields last and only unequip if necessary
                        protagonist.mind.get_weapon_value(o, opponent, melee.get_separation())
                    )
                )

                unequip = []
                for i, item in enumerate(unequip_candidates):
                    if i >= max_hands:
                        break

                    if i < min_hands:
                        # if candidate is worse overall, we may just want to change range instead
                        change_desire = 1.0 + protagonist.mind.get_weapon_change_desire(item, candidate, opponent)
                        # print(f'{item}->{candidate}: {change_desire}')
                        if random.random() > change_desire:
                            change_weapon = False
                            break
                    elif item.is_shield():
                        break
                    else:
                        change_desire = protagonist.mind.get_weapon_change_desire(item, candidate, opponent, melee.get_separation())
                        if random.random() > change_desire:
                            break

                    unequip.append(item)

            elif isinstance(candidate, BodyPart):
                # if candidate is worse overall, we may just want to change range instead
                item = protagonist.inventory.get_item_in_slot(candidate)
                change_desire = 1.0 + protagonist.mind.get_switch_attack_desire(
                    protagonist.mind.get_weapon_value(item, opponent), candidate_score,
                )
                # print(f'{item}->{candidate}: {change_desire}')
                if random.random() > change_desire:
                    change_weapon = False
                unequip = [item]
                candidate = None
            else:
                raise ValueError

            if change_weapon:
                return SwitchHeldItemAction(candidate, *unequip)

    # change range?
    desired_ranges = tactics.get_melee_range_priority(opponent)
    best_range = max(
        desired_ranges, default=None, key=lambda r: (desired_ranges[r], 1 if r == melee.get_separation() else 0, r),
    )
    if best_range is not None and best_range != melee.get_separation():
        change_desire = tactics.get_range_change_desire(opponent, melee.get_separation(), best_range)
        print(f'{protagonist} range change desire: {change_desire:.2f}')
        if change_desire > 0 and random.random() < change_desire:
            return ChangeMeleeRangeAction(opponent, best_range)

    if any(attack.can_attack(melee.get_separation()) for attack in protagonist.get_melee_attacks()):
        return MeleeCombatAction(opponent)

    return None