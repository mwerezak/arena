"""
Arena mode: individual creature combat
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from core.action import ActionLoop
from core.creature import Creature
from core.creature.tactics import SKILL_FACTOR
from core.creature.combat import *

if TYPE_CHECKING:
    from core.creature.inventory import Inventory
    from core.creature.combat import MeleeCombat
    from core.combat.attack import MeleeAttackTemplate
    from core.action import Action, Entity

def get_attack_value(creature: Creature, attack: MeleeAttackTemplate) -> float:
    return attack.damage.mean() * SKILL_FACTOR[creature.get_skill_level(attack.combat_test)]

def try_equip_best_weapons(creature: Creature) -> None:
    inventory = creature.inventory
    inventory.unequip_all()

    weapon_value = {}
    for item in inventory:
        if item.is_weapon():
            best_value = max((get_attack_value(creature, attack) for attack in item.get_melee_attacks(creature)), default=None)
            if best_value is not None:
                weapon_value[item] = best_value

    for item in sorted(weapon_value.keys(), key=lambda k: weapon_value[k], reverse=True):
        if len(list(inventory.get_empty_slots())) == 0:
            break
        inventory.try_equip_item(item)

    ## if there are any left over hands, increase hand count of existing weapons
    for item in sorted(inventory.get_held_items(), key=lambda k: weapon_value[k], reverse=True):
        if len(list(inventory.get_empty_slots())) == 0:
            break
        _, max_hands = item.get_required_hands(creature)
        inventory.try_equip_item(item, use_hands=max_hands)

def print_held_items(inventory: Inventory) -> None:
    for item in inventory.get_held_items():
        print(item, ':', *inventory.get_item_held_by(item))

def print_melee_attacks(creature: Creature) -> None:
    for attack in creature.get_melee_attacks():
        print(attack)

class Arena:
    def __init__(self, loop: ActionLoop, melee: MeleeCombat):
        self.melee = melee  # for now, just process a single melee engagement
        self.action_loop = loop

    def next_turn(self) -> None:
        for idle in self.action_loop.get_idle_entities():
            action = self.get_next_action(idle)
            if action is not None:
                idle.set_current_action(action)

        print(f'Tick: {self.action_loop.elapsed:.1f}')
        self.action_loop.resolve_next()
        print()

    def get_next_action(self, entity: Entity) -> Optional[Action]:
        if isinstance(entity, Creature):
            opponents = {
                o : entity.tactics.get_melee_threat_value(o) for o in entity.get_melee_opponents()
            }

            opponent = max(opponents, key=lambda k: opponents[k], default=None)
            if opponent is not None:
                melee = entity.get_melee_combat(opponent)
                desired_ranges = entity.tactics.get_melee_range_priority(opponent)
                best_range = max(desired_ranges, key=lambda k: desired_ranges[k], default=None)
                if best_range is not None and best_range != melee.separation:
                    return ChangeMeleeRangeAction(opponent, best_range)
                else:
                    return MeleeCombatAction(opponent)
        return None



if __name__ == '__main__':
    from defines.species import SPECIES_GNOLL, SPECIES_GOBLIN
    from core.creature.combat import join_melee_combat
    #from core.combat.tactics import *

    from defines.units.wildalliance import *
    from defines.units.barbarians import *
    from defines.units.wildalliance import CREATURE_SATYR_WARRIOR

    loop = ActionLoop()

    def add_creature(template):
        c = Creature(template)
        try_equip_best_weapons(c)
        c.set_action_loop(loop)
        return c

    gnoll = add_creature(CREATURE_GNOLL_WARRIOR)
    goblin = add_creature(CREATURE_GOBLIN_SPEARMAN)
    satyr = add_creature(CREATURE_SATYR_WARRIOR)

    melee = join_melee_combat(gnoll, goblin)

    arena = Arena(loop, melee)
    arena.next_turn()
    # arena.next_turn()
    # arena.next_turn()

