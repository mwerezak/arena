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

class CombatSkillClass(Enum):
    Blade    = 'Blades'
    Axe      = 'Axes'
    Polearm  = 'Polearms'
    Mace     = 'Maces'
    Bow      = 'Bows'
    Crossbow = 'Crossbows/Firearms'
    Unarmed  = 'Unarmed'
    Thrown   = 'Thrown Weapons'
    Shield   = 'Shields'
    Lance    = 'Lances'
    Sling    = 'Slings'

    @property
    def name(self) -> str:
        return self.value

class CombatTest(Contest):
    def __init__(self, skill_class: CombatSkillClass, key_attr: Iterable[str]):
        super().__init__(skill_class.name, key_attr)

## Melee
SKILL_BLADE    = CombatTest(CombatSkillClass.Blade,    ['STR', 'DEX'])
SKILL_AXE      = CombatTest(CombatSkillClass.Axe,      ['STR', 'DEX'])
SKILL_POLEARM  = CombatTest(CombatSkillClass.Polearm,  ['STR', 'DEX'])
SKILL_MACE     = CombatTest(CombatSkillClass.Mace,     ['STR', 'DEX'])
SKILL_UNARMED  = CombatTest(CombatSkillClass.Unarmed,  ['STR', 'DEX'])
SKILL_SHIELD   = CombatTest(CombatSkillClass.Shield,   ['STR', 'DEX'])
SKILL_LANCE    = CombatTest(CombatSkillClass.Lance,    ['STR', 'DEX'])

## Ranged
SKILL_THROWN   = CombatTest(CombatSkillClass.Thrown,   ['STR', 'DEX'])
SKILL_BOW      = CombatTest(CombatSkillClass.Bow,      ['STR', 'DEX'])

SKILL_SLING    = CombatTest(CombatSkillClass.Sling,    ['DEX', 'DEX'])
SKILL_CROSSBOW = CombatTest(CombatSkillClass.Crossbow, ['DEX', 'DEX'])

## Skill Levels

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
        return self.value - 1

    @property
    def critical_mod(self) -> int:
        return self.value - 1

    def __str__(self) -> str:
        return _LEVEL_NUMERALS[self.value - 1]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value})'


