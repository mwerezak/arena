"""
Arena mode: individual creature combat
"""
from typing import Optional

from core.creature import Creature
from core.creature.combat import MeleeCombat
from core.action import ActionLoop, Action, Entity

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

    def get_next_action(self, entity: Entity) -> Optional[Action]:
        pass

if __name__ == '__main__':
    from defines.species import SPECIES_HUMAN
    from core.creature.combat import create_melee_combat

    loop = ActionLoop()
    a = Creature(SPECIES_HUMAN, loop)
    b = Creature(SPECIES_HUMAN, loop)
    melee = create_melee_combat(a, b)

    arena = Arena(loop, melee)