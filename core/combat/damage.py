from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.dice import DicePool

class DamageType(Enum):
    Slashing = 'slashing'
    Puncture = 'puncture'
    Bludgeon = 'bludgeon'

    def format_type_code(self) -> str:
        return self.value[0]

def format_damage(damage: DicePool, armpen: DicePool, damtype: DamageType) -> str:
    # noinspection PyTypeChecker
    if armpen.max() > 0:
        return f'[{damage}/{armpen}*] ({damtype.format_type_code()})'
    return f'[{damage}]{damtype.format_type_code()}'