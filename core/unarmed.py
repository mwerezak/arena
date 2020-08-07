import math
from typing import Iterable, Type, Mapping, Optional

from core.dice import dice, DicePool
from core.combat.damage import DamageType
from core.combat.criticals import CriticalEffect
from core.combat.attack import MeleeAttack
from core.constants import SizeCategory, MeleeRange
from core.constants import *

## min,max reach at Medium size
BASE_MAX_REACH = 1.0   # REACH_SHORT
BASE_MIN_REACH = 1.0/3 # REACH_CLOSE

_DAMAGE_TABLE = {
      0 : dice(0),
      1 : dice(1),
      2 : dice(1,2),
      4 : dice(1,3),
      8 : dice(1,4), # medium size
     16 : dice(1,6),
     24 : dice(1,8),
     32 : dice(1,10),
     40 : dice(1,12),
     48 : dice(1,10) + dice(1,3),
     56 : dice(1,12) + dice(1,3),
     64 : dice(1,8)  + dice(2,4),
     72 : dice(1,10) + dice(2,4),
     80 : dice(1,12) + dice(2,4),
     88 : dice(1,10) + dice(2,6),
     96 : dice(1,12) + dice(2,6),
    104 : dice(1,10) + dice(2,8),
    112 : dice(1,12) + dice(2,8),
    120 : dice(2,8)  + dice(3,4),
    128 : dice(5,6),
}

_ARMOR_PEN_TABLE = {
      0 : None,
      1 : -dice(1,8),
      2 : -dice(1,6),
      4 : -dice(1,4),
      8 : -dice(1,3),
     16 : -dice(1),
     24 : dice(0),
     32 : dice(1),
     40 : dice(1,3),
     48 : dice(1,4),
     56 : dice(1,6),
     64 : dice(1,8),
     72 : dice(1,10),
     80 : dice(1,12),
     88 : dice(1,10) + dice(1,3),
     96 : dice(1,12) + dice(1,3),
    104 : dice(1,8)  + dice(2,4),
    112 : dice(1,10) + dice(2,4),
    120 : dice(1,12) + dice(2,4),
    128 : dice(1,10) + dice(2,6),
}

def _table_lookup(table: Mapping[int, DicePool], size: float) -> DicePool:
    items = sorted((abs(size-s), s) for s,v in table.items())
    _, k = items[0]
    return table[k]

class NaturalWeapon:
    def __init__(self, name: str, damtype: DamageType,
                force_mod: float = 0, reach_mod: float = 0, damage_mod: float = 0, armor_pen: Optional[float] = None,
                criticals: Iterable[Type[CriticalEffect]] = None):
        self.name = name
        self.damtype = damtype
        self.reach_mod = reach_mod
        self.force_mod = force_mod  # affects both damage and armor penetration as well
        self.damage_mod = damage_mod
        self.armor_pen = armor_pen
        self.criticals = tuple(criticals) if criticals is not None else ()

    def create_attack(self, size: int) -> MeleeAttack:
        rel_size = float(size)/float(SizeCategory.Medium.to_size())
        size_step = math.log2(rel_size)

        reach_size = 2**size_step
        max_reach = BASE_MAX_REACH * reach_size + self.reach_mod
        min_reach = BASE_MIN_REACH * reach_size + self.reach_mod

        damage_size = 8 * 2**(size_step + self.damage_mod + self.force_mod)
        damage = _table_lookup(_DAMAGE_TABLE, damage_size)

        armor_pen = None
        if self.damtype == DamageType.Bludgeon or self.armor_pen is not None:
            armpen_size = 8 * 2**(size_step + (self.armor_pen or 0) + self.force_mod)
            armor_pen = _table_lookup(_ARMOR_PEN_TABLE, armpen_size)

        return MeleeAttack(
            name = self.name,
            reach = (MeleeRange(round(max_reach)), MeleeRange(round(min_reach))),
            force = FORCE_MEDIUM.get_step(round(size_step + self.force_mod)),
            damtype = self.damtype,
            damage = damage,
            armor_pen = armor_pen,
            criticals = self.criticals,
        )

if __name__ == '__main__':
    def print_attack(attack: MeleeAttack):
        print(f'*** {attack.name} ***')
        print(f'force: {attack.force}')
        print(f'reach: {attack.max_reach}-{attack.min_reach}')
        print(f'damage: {attack.damage}' + (f'/{attack.armor_pen}*' if attack.armor_pen is not None else ''))

    UNARMED_PUNCH = NaturalWeapon('Punch', DamageType.Bludgeon, force_mod = -1)
    print_attack(UNARMED_PUNCH.create_attack(8))

    UNARMED_KICK = NaturalWeapon('Kick', DamageType.Bludgeon, force_mod = -1, reach_mod= 1)
    print_attack(UNARMED_KICK.create_attack(8))

    UNARMED_BITE = NaturalWeapon('Bite', DamageType.Puncture, damage_mod=1, reach_mod=-1)
    print_attack(UNARMED_BITE.create_attack(16))