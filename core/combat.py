from enum import Enum
from typing import TYPE_CHECKING, Tuple
from core.melee.attack import MeleeRange

if TYPE_CHECKING:
    from core.creature import Creature

class DamageType(Enum):
    Slashing = 'slashing'
    Puncture = 'puncture'
    Bludgeon = 'bludgeon'

class MeleeCombat:
    combatants: Tuple['Creature', 'Creature']
    separation: MeleeRange