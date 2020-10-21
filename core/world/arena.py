"""
Arena mode: individual creature combat
"""
from __future__ import annotations

from core.creature.actions import *
from core.creature.mind.combat import try_equip_best_weapons
from core.combat.melee import *

if TYPE_CHECKING:
    from core.creature.inventory import Inventory
    from core.combat.melee import MeleeCombat

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


