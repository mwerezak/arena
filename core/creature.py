from enum import Enum
from core.bodyplan import Morphology

class SizeCategory(Enum):
    Tiny   =  2
    Small  =  4
    Medium =  8
    Large  = 16
    Huge   = 32

class PrimaryAttribute(Enum):
    STR = 'strength'
    CON = 'constitution'
    DEX = 'dexterity'
    INT = 'intelligence'
    POW = 'power'


class Creature:
    def __init__(self):
        self.health = 8
        self.template = ...

class CreatureTemplate:
    name: str
    bodyplan: Morphology
    size: int

    def __init__(self):
        self.name = ...
        self.bodyplan = ...
        self.size = ...
        self.stats = ...
        # natural armor
        # natural weapons
        # equipment slots / inventory
        # traits and other qualities

