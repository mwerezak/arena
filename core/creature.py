from enum import Enum
from typing import Mapping, Union

from core.util import IntClass
from core.bodyplan import Morphology

class CreatureSize(IntClass):
    def __init__(self, value: int):
        super().__init__(max(value, 0))

    @property
    def category(self) -> 'SizeCategory':
        _, closest = min((abs(cat.size - self), cat) for cat in SizeCategory)
        return closest

    def __str__(self) -> str:
        return f'{self.category.name.lower()} ({self.value:d})'

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

class CreatureTemplate:
    name: str
    bodyplan: Morphology
    size: CreatureSize
    stats: Mapping[PrimaryAttribute, int]

    def __init__(self):
        self.name = ...
        self.bodyplan = ...
        self.size = ...
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
        return self.size.value + self.get_attribute(PrimaryAttribute.CON)

