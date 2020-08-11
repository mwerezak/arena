"""
Contests are various distinct categories under which creatures may be required to make differential or solo tests of
their ability. Each contest has two (not necessarily distinct) key PrimaryAttributes that contribute to the contest.
Creatures may also have traits that grant a certain level of expertise (valid levels 1-5) in a certain contest types.
"""

from enum import Enum
from typing import Iterable, Sequence
from core.constants import PrimaryAttribute

class Contest:
    def __init__(self, name: str, key_attr: Iterable[str]):
        self.name = name
        self.key_attr: Sequence[PrimaryAttribute] = tuple(PrimaryAttribute[s] for s in key_attr)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name}>'

## Standard Contest Types

SKILL_EVADE      = Contest('Evade',      ['DEX', 'DEX'])
SKILL_ENDURANCE  = Contest('Endurance',  ['CON', 'CON'])
SKILL_WILLPOWER  = Contest('Willpower',  ['POW', 'POW'])
SKILL_PERCEPTION = Contest('Perception', ['INT', 'POW'])
SKILL_STEALTH    = Contest('Stealth',    ['DEX', 'INT'])
SKILL_RIDING     = Contest('Riding',     ['DEX', 'POW'])

# not sure if these will be used
SKILL_ATHLETICS  = Contest('Athletics',  ['STR', 'SIZ'])
SKILL_BRAWN      = Contest('Brawn',      ['STR', 'SIZ'])

## Combat Contest Types

class CombatTest(Contest):
    pass

## Melee
SKILL_BLADE    = CombatTest('Blades',   ['STR', 'DEX'])
SKILL_AXE      = CombatTest('Axes',     ['STR', 'DEX'])
SKILL_POLEARM  = CombatTest('Polearms', ['STR', 'DEX'])
SKILL_MACE     = CombatTest('Maces',    ['STR', 'DEX'])
SKILL_UNARMED  = CombatTest('Unarmed',  ['STR', 'DEX'])
SKILL_SHIELD   = CombatTest('Shields',  ['STR', 'DEX'])
SKILL_LANCE    = CombatTest('Lances',   ['STR', 'DEX'])

## Ranged
SKILL_THROWN   = CombatTest('Thrown Weapons', ['STR', 'DEX'])
SKILL_BOW      = CombatTest('Bows',           ['STR', 'DEX'])

SKILL_SLING    = CombatTest('Slings',             ['DEX', 'DEX'])
SKILL_CROSSBOW = CombatTest('Crossbows/Firearms', ['DEX', 'DEX'])

class CombatSkillClass(Enum):
    Blade    = SKILL_BLADE
    Axe      = SKILL_AXE
    Polearm  = SKILL_POLEARM
    Mace     = SKILL_MACE
    Bow      = SKILL_BOW
    Crossbow = SKILL_CROSSBOW
    Unarmed  = SKILL_UNARMED
    Thrown   = SKILL_THROWN
    Shield   = SKILL_SHIELD
    Lance    = SKILL_LANCE
    Sling    = SKILL_SLING

    @property
    def contest(self) -> CombatTest:
        return self.value

    @property
    def contest_name(self) -> str:
        return self.contest.name

## Skill Levels

_LEVEL_NUMERALS = ['I', 'II', 'III', 'IV', 'V']

# by default skill level is 0, which grants no bonuses
class SkillLevel(Enum):
    none       = 0  # because None is a reserved word
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
        return self.value - 1

    @property
    def critical_mod(self) -> int:
        return self.value - 1

    def __str__(self) -> str:
        return _LEVEL_NUMERALS[self.value - 1]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value})'


