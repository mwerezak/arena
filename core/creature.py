from enum import Enum
from typing import Union, MutableMapping

from core.util import IntClass
from core.bodyplan import Morphology
from core.combat import MeleeCombat

class CreatureSize(IntClass):
    def __new__(cls, value: int):
        return super().__new__(cls, max(value, 0))

    @property
    def category(self) -> 'SizeCategory':
        _, closest = min((abs(cat.size - self), cat) for cat in SizeCategory)
        return closest

    def __str__(self) -> str:
        return f'{self.category.name.lower()} ({self:d})'

class SizeCategory(Enum):
    Tiny   = CreatureSize(2)
    Small  = CreatureSize(4)
    Medium = CreatureSize(8)
    Large  = CreatureSize(16)
    Huge   = CreatureSize(32)

    @property
    def size(self) -> CreatureSize:
        return self.value

class PrimaryAttribute(Enum):
    STR = 'strength'
    CON = 'constitution'
    DEX = 'dexterity'
    INT = 'intelligence'
    POW = 'power'

class Creature:
    health: float
    template: 'CreatureTemplate'
    melee_combat: MutableMapping['Creature', 'MeleeCombat']
    # get_engage_range() -> MeleeRange

class CreatureTemplate:
    name: str
    bodyplan: Morphology
    size: CreatureSize
    #stats: Mapping[PrimaryAttribute, int]

    def __init__(self, name: str, bodyplan: Morphology, size: CreatureSize):
        self.name = name
        self.bodyplan = bodyplan
        self.size = size
        self.stats = ...
        # natural armor
        # natural weapons
        # equipment slots / inventory
        # traits and other qualities

    def get_attribute(self, attr: Union[str, PrimaryAttribute]) -> int:
        if not isinstance(attr, PrimaryAttribute):
            attr = PrimaryAttribute[attr]
        return self.stats[attr]

    @property
    def max_health(self) -> int:
        return self.size + self.get_attribute(PrimaryAttribute.CON)

    @property
    def initiative(self) -> int:
        raise NotImplemented  # higher initiative helps to resolve action interruptions in this creature's favor

    # interrupt success
    # initiative = interrupting.owner.initiative - interrupted.owner.initiative
    # priority = interrupted.windup/interrupting.windup + (math.log(1.5) * initiative)
    # interrupt_chance = 1.0/(math.exp(-priority) + 1.0)