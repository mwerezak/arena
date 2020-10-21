"""
Arena mode: individual creature combat
"""
from __future__ import annotations

from core.creature.actions import *
from core.combat.melee import *

from core.creature.mind.tactics import SKILL_FACTOR

if TYPE_CHECKING:
    from core.creature.inventory import Inventory
    from core.combat.melee import MeleeCombat
    from core.combat.attack import MeleeAttackTemplate

def print_held_items(inventory: Inventory) -> None:
    for item in inventory.get_held_items():
        print(item, ':', *inventory.get_item_held_by(item))

def print_melee_attacks(creature: Creature) -> None:
    for attack in creature.get_melee_attacks():
        print(attack)

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

class Arena:
    def __init__(self, loop: ActionLoop, melee: MeleeCombat):
        self.melee = melee  # for now, just process a single melee engagement
        self.action_loop = loop

    def next_turn(self) -> None:
        for entity in list(self.action_loop.get_entities()):
            if isinstance(entity, Creature) and not entity.is_conscious():
                self.action_loop.remove_entity(entity)
                if entity in self.melee.combatants:
                    self.melee.break_engagement()

        for idle in self.action_loop.get_idle_entities():
            if isinstance(idle, Creature):
                action = idle.mind.next_combat_action()
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
    from core.action import ActionLoop
    from core.creature import Creature

    from defines.units.wildalliance import *
    from defines.units.barbarians import *
    from defines.units.feudal import *

    loop = ActionLoop()

    def add_creature(template):
        #t = CreatureTemplate(template=template)
        #t.set_loadout(Loadout([WEAPON_CLUB]))
        c = Creature(template)
        try_equip_best_weapons(c)
        c.set_action_loop(loop)
        return c

    gnoll = add_creature(CREATURE_GNOLL_WARRIOR)
    gnoll2 = add_creature(CREATURE_GNOLL_WARRIOR)
    goblin = add_creature(CREATURE_GOBLIN_ENFORCER)
    gob_inf = add_creature(CREATURE_GOBLIN_SPEARMAN)
    satyr = add_creature(CREATURE_SATYR_WARDEN)
    satyr_brave = add_creature(CREATURE_SATYR_WARRIOR)
    orc = add_creature(CREATURE_ORC_BARBARIAN)
    orc2 = add_creature(CREATURE_ORC_BARBARIAN)
    ogre = add_creature(CREATURE_OGRE_BRUTE)
    mino = add_creature(CREATURE_MINOTAUR_WARRIOR)
    # orc.name = 'Orc 1'
    # orc2.name = 'Orc 2'
    spearman = add_creature(CREATURE_SERGEANT_SPEARMAN)
    ranger = add_creature(CREATURE_OUTLAND_RANGER)

    melee = join_melee_combat(satyr_brave, spearman)
    # melee.change_separation(MeleeRange(0))
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
    # mino.get_bodypart('r_arm').injure_part()
    # orc.apply_wounds(12)
    # while True:
    #     next_turn()


