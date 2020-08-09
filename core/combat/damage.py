from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

class DamageType(Enum):
    Slashing = 'slashing'
    Puncture = 'puncture'
    Bludgeon = 'bludgeon'

