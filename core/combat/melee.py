from typing import TYPE_CHECKING, Tuple
from core.constants import MeleeRange

if TYPE_CHECKING:
    from core.creature import Creature

class MeleeCombat:
    combatants: Tuple['Creature', 'Creature']
    separation: MeleeRange

    def __init__(self, a: Creature, b: Creature):
        self.combatants = (a, b)
        self.separation = max(a.get_melee_engage_distance(), b.get_melee_engage_distance())