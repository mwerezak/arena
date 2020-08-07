
from typing import TYPE_CHECKING, Tuple, Collection, Type, Iterable, Optional

from core.util import IntClass
from core.dice import DicePool
from core.critical import CriticalEffect

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

    CLOSE = __new__(0)

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
                 armor_pen: Optional[DicePool] = None,
                 criticals: Iterable[Type[CriticalEffect]] = None):
        self.name = name
        self.max_reach = max(reach)
        self.min_reach = min(reach)
        self.force = force
        self.damtype = damtype
        self.damage = damage
        self.armor_pen = armor_pen
        self.criticals = list(criticals) if criticals is not None else []
