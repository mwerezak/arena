
from typing import TYPE_CHECKING, Tuple, Collection, Type, Iterable

from core.util import IntClass
from core.dice import DicePool
from core.melee.critical import CriticalEffect

if TYPE_CHECKING:
    from core.combat import DamageType

class MeleeRange(IntClass):
    __NAMES = [
        'close',
        'short',
        'medium',
        'long',
        'very long',
        'extreme',
    ]

    def __new__(cls, value: int):
        return super().__new__(cls, max(value, 0))

    def __str__(self) -> str:
        if self < len(self.__NAMES):
            return self.__NAMES[self]
        return f'{self.__NAMES[-1]} (+{self - len(self.__NAMES) + 1 :d})'

class AttackForce(IntClass):
    __NAMES = [
        'none',
        'tiny',
        'small',
        'medium',
        'large',
        'overwhelming',
    ]

    def __new__(cls, value: int):
        return super().__new__(cls, max(value, 0))

    def __str__(self) -> str:
        if self < len(self.__NAMES):
            return self.__NAMES[self]
        return f'{self.__NAMES[-1]} (+{self - len(self.__NAMES) + 1 :d})'

## MeleeAttacks

class MeleeAttack:
    name: str
    force: AttackForce
    damtype: 'DamageType'
    damage: DicePool
    criticals: Collection[Type[CriticalEffect]]

    def __init__(self,
                 name: str,
                 reach: Tuple[MeleeRange, MeleeRange],
                 force: AttackForce,
                 damtype: 'DamageType',
                 damage: DicePool,
                 criticals: Iterable[Type[CriticalEffect]] = None):
        self.name = name
        self.max_reach = max(reach)
        self.min_reach = min(reach)
        self.force = force
        self.damtype = damtype
        self.damage = damage
        self.criticals = list(criticals) if criticals is not None else []

## Define certain values for convenience

MeleeRange.CLOSE   = MeleeRange(0)
MeleeRange.SHORT   = MeleeRange(1)
MeleeRange.MEDIUM  = MeleeRange(2)
MeleeRange.LONG    = MeleeRange(3)
MeleeRange.VLONG   = MeleeRange(4)
MeleeRange.EXTREME = MeleeRange(5)

AttackForce.NONE   = AttackForce(0)
AttackForce.TINY   = AttackForce(1)
AttackForce.SMALL  = AttackForce(2)
AttackForce.MEDIUM = AttackForce(3)
AttackForce.LARGE  = AttackForce(4)
AttackForce.OVERWM = AttackForce(5)





