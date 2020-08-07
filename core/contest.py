"""
Contests are various distinct categories under which creatures may be required to make differential or solo tests of
their ability. Each contest has two (not necessarily distinct) key PrimaryAttributes that contribute to the contest.
Creatures may also have traits that grant a certain level of expertise (valid levels 1-5) in a certain contest types.
"""

from enum import Enum
from typing import Iterable, Sequence
from core.creature import PrimaryAttribute

class Contest:
    def __init__(self, name: str, key_attr: Iterable[str]):
        self.name = name
        self.key_attr: Sequence[PrimaryAttribute] = tuple(PrimaryAttribute[s] for s in key_attr)

SKILL_MELEE      = Contest('Melee',      ['STR', 'DEX'])
SKILL_UNARMED    = Contest('Melee',      ['STR', 'DEX'])
SKILL_EVADE      = Contest('Evade',      ['DEX', 'DEX'])
SKILL_ENDURANCE  = Contest('Endurance',  ['CON', 'CON'])
SKILL_WILLPOWER  = Contest('Willpower',  ['POW', 'POW'])
SKILL_ATHLETICS  = Contest('Athletics',  ['STR', 'SIZ'])
SKILL_BRAWN      = Contest('Brawn',      ['STR', 'SIZ'])
SKILL_PERCEPTION = Contest('Perception', ['INT', 'POW'])
SKILL_STEALTH    = Contest('Stealth',    ['DEX', 'INT'])

_LEVEL_NUMERALS = ['I', 'II', 'III', 'IV', 'V']

# by default skill level is 0, which grants no bonuses
class SkillLevel(Enum):
    Competent  = 1
    Proficient = 2
    Talented   = 3
    Expert     = 4
    Master     = 5

    @property
    def dice_bonus(self) -> int:
        return self.value

    @property
    def contest_mod(self) -> int:
        return self.value

    @property
    def critical_mod(self) -> int:
        return self.value

    def __str__(self) -> str:
        return _LEVEL_NUMERALS[self.value - 1]


