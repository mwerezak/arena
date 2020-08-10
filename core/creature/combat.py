from typing import TYPE_CHECKING, Tuple, Optional
from core.constants import MeleeRange

if TYPE_CHECKING:
    from core.creature import Creature

def create_melee_combat(a: 'Creature', b: 'Creature') -> 'MeleeCombat':
    melee = MeleeCombat(a, b)
    a.add_melee_combat(b, melee)
    b.add_melee_combat(a, melee)
    return melee

class MeleeCombat:
    combatants: Tuple['Creature', 'Creature']
    separation: MeleeRange

    def __init__(self, a: 'Creature', b: 'Creature'):
        self.combatants = (a, b)
        self.separation = max(a.get_melee_engage_distance(), b.get_melee_engage_distance())

    def get_opponent(self, combatant: 'Creature') -> Optional['Creature']:
        if combatant == self.combatants[0]:
            return self.combatants[1]
        if combatant == self.combatants[1]:
            return self.combatants[0]
        return None

    def break_engagement(self) -> None:
        self.combatants[0].remove_melee_combat(self.combatants[1])
        self.combatants[1].remove_melee_combat(self.combatants[0])
        del self.combatants