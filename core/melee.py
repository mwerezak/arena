
from typing import Tuple

from core.util import IntClass
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

    def __init__(self, value: int):
        super().__init__(max(value, 0))

    def __str__(self) -> str:
        if self.value < len(self.__NAMES):
            return self.__NAMES[self.value]
        return f'{self.__NAMES[-1]} (+{self.value - len(self.__NAMES) + 1 :d})'


class AttackForce(IntClass):
    __NAMES = [
        'none',
        'tiny',
        'small',
        'medium',
        'large',
        'overwhelming',
    ]

    def __init__(self, value: int):
        super().__init__(max(value, 0))

    def __str__(self) -> str:
        if self.value < len(self.__NAMES):
            return self.__NAMES[self.value]
        return f'{self.__NAMES[-1]} (+{self.value - len(self.__NAMES) + 1 :d})'

## MeleeAttacks

class MeleeAttack:
    name: str
    force: AttackForce
    damage: ...

    def __init__(self, name: str, reach: Tuple[MeleeRange, MeleeRange], force: AttackForce, damage: ...):
        self.name = name
        self.max_reach = max(reach)
        self.min_reach = min(reach)
        self.force = force



# MeleeSpecials
# Modify the results of an attack or produce some special effect


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





