
from enum import IntFlag
from typing import Tuple, Collection

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
    damtype: DamageType
    damage: ...
    specials: Collection[...]

    def __init__(self, name: str, reach: Tuple[MeleeRange, MeleeRange], force: AttackForce, damtype: DamageType, damage: ...):
        self.name = name
        self.max_reach = max(reach)
        self.min_reach = min(reach)
        self.force = force

class CombatUsage(IntFlag):
    Offensive = 0x1
    Defensive = 0x2

class CombatSpecial:
    name: str
    usage: CombatUsage

    # __init__()  - should take parameters needed to resolve the effect of the special in combat

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





