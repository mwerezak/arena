from enum import Enum
from typing import TYPE_CHECKING, Tuple
from core.melee.attack import MeleeRange

if TYPE_CHECKING:
    from core.creature import Creature

class DamageType(Enum):
    slashing = 'slashing'
    puncture = 'puncture'
    bludgeon = 'bludgeon'

class MeleeCombat:
    combatants: Tuple['Creature', 'Creature']
    separation: MeleeRange