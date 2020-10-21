from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional

from core.creature.bodypart import BodyPart
from core.creature.mind.tactics import CombatTactics, get_melee_attack_value
from core.creature.actions import ChangeStanceAction, SwitchHeldItemAction
from core.equipment import Equipment
from core.combat.melee import ChangeMeleeRangeAction, MeleeCombatAction

if TYPE_CHECKING:
    from core.creature import Creature
    from core.creature.actions import CreatureAction
    from core.creature.inventory import Inventory

class CreatureMind(CombatTactics):
    def __init__(self, creature: Creature):
        self.creature = creature
        super(CreatureMind, self).__init__(creature)

    @property
    def inventory(self) -> Inventory:
        return self.creature.inventory

    def next_combat_action(self) -> Optional[CreatureAction]:
        if self.creature.stance < self.creature.max_stance:
            return ChangeStanceAction(self.creature.max_stance)

        # choose opponent
        opponents = { o : self.get_melee_threat_value(o) for o in self.creature.get_melee_opponents() }
        opponent = max(opponents, key=lambda k: opponents[k], default=None)
        if opponent is None:
            return None

        act = self._possibly_switch_weapons(opponent)
        if act is not None:
            return act

        act = self._possibly_change_melee_range(opponent)
        if act is not None:
            return act

        melee = self.creature.get_melee_combat(opponent)
        if any(attack.can_attack(melee.get_separation()) for attack in self.creature.get_melee_attacks()):
            return MeleeCombatAction(opponent)

        return None


    def _possibly_change_melee_range(self, opponent: Creature) -> Optional[CreatureAction]:
        melee = self.creature.get_melee_combat(opponent)

        desired_ranges = self.get_melee_range_priority(opponent)
        best_range = max(
            desired_ranges, default=None, key=lambda r: (desired_ranges[r], 1 if r == melee.get_separation() else 0, r),
        )
        if best_range is not None and best_range != melee.get_separation():
            change_desire = self.get_range_change_desire(opponent, melee.get_separation(), best_range)
            # print(f'{self.creature} range change desire: {change_desire:.2f}')
            if change_desire > 0 and random.random() < change_desire:
                return ChangeMeleeRangeAction(opponent, best_range)


    def _possibly_switch_weapons(self, opponent: Creature) -> Optional[CreatureAction]:
        melee = self.creature.get_melee_combat(opponent)

        # determine available attacks
        attack_values = (
            get_melee_attack_value(attack, self.creature, opponent)
            for attack in self.creature.get_melee_attacks()
            if attack.can_attack(melee.get_separation())
        )
        best_score = max(attack_values, default=0)
        equipped = [*self.inventory.get_held_items()]
        available = (item for item in self.creature.inventory if item.is_weapon() and item not in equipped)
        available = {
            item : value for item in available
            if (value := self.get_weapon_value(item, opponent, melee.get_separation())) > 0
        }

        # look at unarmed attacks that are unavailable due to equipped weapons
        inv = self.creature.inventory
        occupied = [
            bp for bp in inv.get_equip_slots() if (item := inv.get_item_in_slot(bp)) is not None and not item.is_shield()
        ]
        for bp in occupied:
            if self.inventory.get_item_in_slot(bp) is not None:
                value = max((
                    get_melee_attack_value(attack, self.creature, opponent)
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
                    min_hands, max_hands = candidate.get_required_hands(self.creature)

                    unequip_candidates = sorted(
                        self.inventory.get_held_items(),
                        key=lambda o: (
                            1 if o.is_shield() else 0,  # sort shields last and only unequip if necessary
                            self.get_weapon_value(o, opponent, melee.get_separation())
                        )
                    )

                    unequip = []
                    for i, item in enumerate(unequip_candidates):
                        if i >= max_hands:
                            break

                        if i < min_hands:
                            # if candidate is worse overall, we may just want to change range instead
                            change_desire = 1.0 + self.get_weapon_change_desire(item, candidate, opponent)
                            # print(f'{item}->{candidate}: {change_desire}')
                            if random.random() > change_desire:
                                change_weapon = False
                                break
                        elif item.is_shield():
                            break
                        else:
                            change_desire = self.get_weapon_change_desire(item, candidate, opponent, melee.get_separation())
                            if random.random() > change_desire:
                                break

                        unequip.append(item)

                elif isinstance(candidate, BodyPart):
                    # if candidate is worse overall, we may just want to change range instead
                    item = self.inventory.get_item_in_slot(candidate)
                    change_desire = 1.0 + self.get_switch_attack_desire(
                        self.get_weapon_value(item, opponent), candidate_score,
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

        return None

