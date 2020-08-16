"""
Arena mode: individual creature combat
"""
from __future__ import annotations

from core.action import ActionLoop
from core.creature.tactics import SKILL_FACTOR, get_melee_attack_value
from core.creature.actions import *
from core.combat.melee import *

if TYPE_CHECKING:
    from core.creature.inventory import Inventory
    from core.combat.melee import MeleeCombat
    from core.combat.attack import MeleeAttackTemplate


def get_attack_value(creature: Creature, attack: MeleeAttackTemplate) -> float:
    return attack.damage.mean() * SKILL_FACTOR[creature.get_skill_level(attack.combat_test)]

def try_equip_best_weapons(creature: Creature) -> None:
    inventory = creature.inventory
    inventory.unequip_all()

    weapon_value = {}
    for item in inventory:
        if item.is_weapon():
            weapon_value[item] = max((get_attack_value(creature, attack) for attack in item.get_melee_attacks(creature)), default=0.0)

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

def get_next_action(protagonist: Creature) -> Optional[CreatureAction]:
    tactics = protagonist.tactics

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
        item : protagonist.tactics.get_weapon_value(item, opponent, melee.get_separation())
        for item in available
    }

    candidate = max(available.keys(), key=lambda k: available[k],default=None)
    if candidate is not None:
        candidate_score = available[candidate]
        change_desire = min(max(0.0, (candidate_score/best_score-1.0)/2.0), 1.0)

        print(f'{protagonist} weapon change desire: {change_desire:.2f}')
        if change_desire > 0 and random.random() < change_desire:
            min_hands, max_hands = candidate.get_required_hands(protagonist)

            unequip_candidates = sorted(
                protagonist.inventory.get_held_items(),
                key=lambda o: (
                    1 if o.is_shield() else 0, # unequip shields last
                    protagonist.tactics.get_weapon_value(o, opponent, melee.get_separation())
                )
            )
            unequip = []

            change_weapon = True
            for i, item in enumerate(unequip_candidates):
                if i < min_hands:
                    # if candidate is worse overall, we may just want to change range instead
                    change_desire = 1.0 + protagonist.tactics.get_weapon_change_desire(item, candidate, opponent)
                    print(f'{item}->{candidate}: {change_desire}')
                    if random.random() > change_desire:
                        change_weapon = False
                        break
                else:
                    change_desire = protagonist.tactics.get_weapon_change_desire(item, candidate, opponent, melee.get_separation())
                    if random.random() > change_desire:
                        break

                unequip.append(item)

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
        for entity in list(self.action_loop.get_entities()):
            if isinstance(entity, Creature) and not entity.alive:
                self.action_loop.remove_entity(entity)
                if entity in self.melee.combatants:
                    self.melee.break_engagement()

        for idle in self.action_loop.get_idle_entities():
            if isinstance(idle, Creature):
                action = get_next_action(idle)
                if action is not None:
                    idle.set_current_action(action)

        print(f'Tick: {self.action_loop.elapsed} Action Queue:')
        for item in self.action_loop.action_queue:
            print(item.action)
        print()

        self.action_loop.resolve_next()
        print()

if __name__ == '__main__':
    from defines.species import SPECIES_GNOLL, SPECIES_GOBLIN
    from core.combat.melee import join_melee_combat

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
    orc = add_creature(CREATURE_ORC_BARBARIAN)
    orc2 = add_creature(CREATURE_ORC_BARBARIAN)
    mino = add_creature(CREATURE_MINOTAUR_MILITIA)
    # orc.name = 'Orc 1'
    # orc2.name = 'Orc 2'

    melee = join_melee_combat(mino, orc)
    for c in melee.combatants:
        print(c.name, f'({sum(item.cost for item in c.inventory)}sp)')
        print(*c.inventory, sep='\n')
        print()

    arena = Arena(loop, melee)

    def next_turn():
        last_tick = arena.action_loop.get_tick()
        while last_tick == arena.action_loop.get_tick():
            arena.next_turn()
            if arena.action_loop.queued_action_count() == 0:
                break

    next_turn()


