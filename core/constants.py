from enum import Enum
from functools import total_ordering

class PrimaryAttribute(Enum):
    STR = 'Strength'
    CON = 'Constitution'
    SIZ = 'Size'
    DEX = 'Dexterity'
    INT = 'Intelligence'
    POW = 'Power'
    CHA = 'Charisma'

class IntClass(int):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self:d})'

    def get_step(self, step: int) -> 'IntClass':
        return self.__class__(self + step)

class CreatureSize(IntClass):
    def __new__(cls, value: int):
        return super().__new__(cls, max(value, 1))

    def get_category(self) -> 'SizeCategory':
        _, closest = min((abs(cat.size - self), cat) for cat in SizeCategory)
        return closest

    def __str__(self) -> str:
        return f'{self.get_category().name.lower()} ({self:d})'

@total_ordering
class SizeCategory(Enum):
    Fine     = 0
    Tiny     = 1
    Small    = 2
    Medium   = 3
    Large    = 4
    Huge     = 5
    Enormous = 6
    Colossal = 7

    def to_size(self) -> CreatureSize:
        return CreatureSize(2**self.value)

    def __lt__(self, other: 'SizeCategory') -> bool:
        return self.value < other.value

    def get_step(self, step: int) -> 'SizeCategory':
        return SizeCategory(min(max(self.Fine.value, self.value + step), self.Colossal.value))

class MeleeRange(IntClass):
    __NAMES = [
        'Close',
        'Short',
        'Medium',
        'Long',
        'Very Long',
        'Extreme',
    ]

    def __new__(cls, value: int):
        return super().__new__(cls, max(value, 0))

    def __str__(self) -> str:
        if self < len(self.__NAMES):
            return self.__NAMES[self]
        return f'{self.__NAMES[-1]} (+{self - len(self.__NAMES) + 1 :d})'

class AttackForce(IntClass):
    __NAMES = [
        'None',
        'Tiny',
        'Small',
        'Medium',
        'Large',
        'Overwhelming',
    ]

    def __new__(cls, value: int):
        return super().__new__(cls, max(value, 0))

    def __str__(self) -> str:
        if self < len(self.__NAMES):
            return self.__NAMES[self]
        return f'{self.__NAMES[-1]} (+{self - len(self.__NAMES) + 1 :d})'

REACH_CLOSE   = MeleeRange(0)
REACH_SHORT   = MeleeRange(1)
REACH_MEDIUM  = MeleeRange(2)
REACH_LONG    = MeleeRange(3)
REACH_VLONG   = MeleeRange(4)
REACH_EXTREME = MeleeRange(5)

FORCE_NONE   = AttackForce(0)
FORCE_TINY   = AttackForce(1)
FORCE_SMALL  = AttackForce(2)
FORCE_MEDIUM = AttackForce(3)
FORCE_LARGE  = AttackForce(4)
FORCE_OVERWM = AttackForce(5)

__all__ = [
    'PrimaryAttribute', 'CreatureSize', 'SizeCategory', 'MeleeRange', 'AttackForce',
    'REACH_CLOSE', 'REACH_SHORT', 'REACH_MEDIUM', 'REACH_LONG', 'REACH_VLONG', 'REACH_EXTREME',
    'FORCE_NONE', 'FORCE_TINY', 'FORCE_SMALL', 'FORCE_MEDIUM', 'FORCE_LARGE', 'FORCE_OVERWM',
]