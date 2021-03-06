"""
Contests are various distinct categories under which creatures may be required to make differential or solo tests of
their ability. Each contest has two (not necessarily distinct) key PrimaryAttributes that contribute to the contest.
Creatures may also have traits that grant a certain level of expertise (valid levels 1-5) in a certain contest types.
"""
from __future__ import annotations

import itertools
from enum import Enum
from collections import Counter
from functools import lru_cache, total_ordering
from typing import TYPE_CHECKING, Iterable, Sequence, Mapping, NamedTuple

from core.constants import PrimaryAttribute
from core.dice import dice
from core.creature.traits import FinesseTrait
if TYPE_CHECKING:
    from core.creature import Creature

_PRECALC_TABLES = False
_LEVEL_NUMERALS = ['I', 'II', 'III', 'IV', 'V']

# by default skill level is 0, which grants no bonuses
@total_ordering
class SkillLevel(Enum):
    none       = 0  # because None is a reserved word
    Competent  = 1
    Proficient = 2
    Talented   = 3
    Expert     = 4
    Master     = 5

    @property
    def bonus_dice(self) -> int:
        return self.value

    @property
    def contest_mod(self) -> int:
        return 0

    @property
    def critical_mod(self) -> int:
        return self.value - 1

    def __lt__(self, other: SkillLevel) -> bool:
        return self.value < other.value

    def __str__(self) -> str:
        return _LEVEL_NUMERALS[self.value - 1]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value})'

class Contest:
    BASE_DICE = 3
    BASE_SIDES = 8

    CRIT_THRESH = 5
    MAX_CRIT = 3

    def __init__(self, name: str, key_attr: Iterable[str], innate: bool = False):
        self.name = name
        self.key_attr: Sequence[PrimaryAttribute] = tuple(PrimaryAttribute[s] for s in key_attr)
        self.innate = innate  # innate skills cannot recieve a negative modifier for low skill level

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name}>'

    def __str__(self) -> str:
        return self.name

    def get_attribute_modifier(self, protagonist: Creature) -> int:
        return sum(protagonist.get_attribute(attr) for attr in self.key_attr)

    def get_skill_modifier(self, skill_level: SkillLevel) -> int:
        modifier = skill_level.contest_mod
        if self.innate and modifier < 0:
            return 0
        return modifier

    def get_crit_modifier(self, skill_level: SkillLevel) -> int:
        modifier = skill_level.critical_mod
        if self.innate and modifier < 0:
            return 0
        return modifier

    def get_success_chance(self, protagonist: Creature, target: int) -> float:
        skill_level = protagonist.get_skill_level(self)
        target -= self.get_attribute_modifier(protagonist) + self.get_skill_modifier(skill_level)

        roll_table = get_roll_table(skill_level.bonus_dice)
        return sum(p for roll, p in roll_table.items() if roll > target)

    @staticmethod
    def get_opposed_chance(protagonist: Creature, pro_contest: Contest,
                           antagonist: Creature, ant_contest: Contest = None,
                           modifier: int = 0):
        ant_contest = ant_contest or pro_contest
        pro_level = protagonist.get_skill_level(pro_contest)
        pro_mod = pro_contest.get_attribute_modifier(protagonist) + pro_contest.get_skill_modifier(pro_level)

        ant_level = antagonist.get_skill_level(ant_contest)
        ant_mod = ant_contest.get_attribute_modifier(antagonist) + ant_contest.get_skill_modifier(ant_level)

        target = ant_mod - pro_mod - modifier
        roll_table = get_opposed_roll_table(pro_level.bonus_dice, ant_level.bonus_dice)
        return sum(p for result, p in roll_table.items() if result > target)

class DifficultyGrade(Enum):
    VeryEasy   = +5
    Easy       = +2
    Standard   = +0
    Hard       = -2
    Formidable = -5
    Herculean  = -10

    @property
    def contest_mod(self) -> int:
        return self.value

    @property
    def critical_mod(self) -> int:
        return min(self.value, 0) # difficulty grade can make it harder to critical, but not easier

    def to_modifier(self) -> ContestModifier:
        return ContestModifier(self.contest_mod, self.critical_mod)

    def get_step(self, step: int) -> DifficultyGrade:
        if step == 0:
            return self
        values = list(DifficultyGrade)
        index = values.index(self) + step
        return values[min(max(0, index), len(values) - 1)]

class ContestModifier(NamedTuple):
    contest: int = 0
    critical: int = 0

    def __add__(self, other: ContestModifier) -> ContestModifier:
        return ContestModifier(
            self.contest + other.contest,
            self.critical + other.critical,
        )

    def __sub__(self, other: ContestModifier) -> ContestModifier:
        return self + (-other)

    def __neg__(self) -> ContestModifier:
        return ContestModifier(self.contest * -1, self.critical * -1)

class ContestResult:
    base_result: Sequence[int]
    base_total: int

    def __init__(self, protagonist: Creature, contest: Contest, modifier: ContestModifier = ContestModifier()):
        self.contest = contest
        self.protagonist = protagonist
        self.skill_level = protagonist.get_skill_level(contest)
        self.modifier = modifier
        self.reroll()

    def reroll(self) -> None:
        contest_dice = dice(Contest.BASE_DICE + self.skill_level.bonus_dice, Contest.BASE_SIDES)
        self.base_result = sorted(contest_dice.get_roll(), reverse=True)[:Contest.BASE_DICE]
        self.base_total = sum(self.base_result)

    # the modifier from skill level - does not include the situational modifier
    @property
    def contest_modifier(self) -> int:
        return self.contest.get_attribute_modifier(self.protagonist) + self.contest.get_skill_modifier(self.skill_level)

    @property
    def contest_total(self) -> int:
        return self.base_total + self.contest_modifier + self.modifier.contest

    # the modifier from skill level - does not include the situational modifier
    @property
    def crit_modifier(self) -> int:
        return self.contest.get_crit_modifier(self.skill_level)

    @property
    def crit_total(self) -> int:
        return self.base_total + self.crit_modifier + self.modifier.critical

    def get_crit_level(self, versus: int) -> int:
        crit = int((self.crit_total - versus - 1) / Contest.CRIT_THRESH)
        return min(max(0, crit), Contest.MAX_CRIT)

class UnopposedResult:
    DEFAULT_TARGET = 13  # 50% chance of success

    def __init__(self, result: ContestResult, target: int = DEFAULT_TARGET):
        self.result = result
        self.target = target

    @property
    def protagonist(self) -> Creature:
        return self.result.protagonist

    @property
    def pro_result(self) -> ContestResult:
        return self.result

    @property
    def success(self) -> bool:
        return self.result.contest_total > self.target

    @property
    def crit_level(self) -> int:
        return self.result.get_crit_level(self.target)

    def format_details(self) -> str:
        result = self.result
        mod_text = f'({result.modifier.contest:+d})' if result.modifier.contest != 0 else ''
        success_text = 'SUCCESS' if self.success else 'FAIL'
        return (
            f'[Test] {result.contest} RESULT: {result.base_total}{result.contest_modifier:+d}{mod_text}={result.contest_total} '
            f'vs {self.target} {success_text} (crit level: {self.crit_level})'
        )

class OpposedResult:
    def __init__(self, pro_result: ContestResult, ant_result: ContestResult):
        self.pro_result = pro_result  # protagonist
        self.ant_result = ant_result  # antagonist

    @property
    def protagonist(self) -> Creature:
        return self.pro_result.protagonist

    @property
    def antagonist(self) -> Creature:
        return self.ant_result.protagonist

    @property
    def success(self) -> bool:
        return self.pro_result.contest_total > self.ant_result.contest_total

    @property
    def crit_level(self) -> int:
        if self.success:
            return self.pro_result.get_crit_level(self.ant_result.crit_total)
        else:
            return self.ant_result.get_crit_level(self.pro_result.crit_total)

    def format_details(self) -> str:
        p, a = self.pro_result, self.ant_result
        pro_mod_text = f'({p.modifier.contest:+d})' if p.modifier.contest != 0 else ''
        ant_mod_text = f'({a.modifier.contest:+d})' if a.modifier.contest != 0 else ''
        success_text = 'SUCCESS' if self.success else 'FAIL'
        return (
            f'[Opposed Contest] {p.contest} vs {a.contest} '
            f'RESULT: {p.base_total}{p.contest_modifier:+d}{pro_mod_text}={p.contest_total} vs '
            f'{a.base_total}{a.contest_modifier:+d}{ant_mod_text}={a.contest_total} '
            f'{success_text} (crit level: {self.crit_level})'
        )

@lru_cache
def get_roll_table(bonus_dice: int) -> Mapping[int, float]:
    if bonus_dice > 5:
        raise ValueError  # it's going to take too long

    result = Counter()
    for roll in itertools.product(list(range(1, Contest.BASE_SIDES + 1)), repeat = Contest.BASE_DICE + bonus_dice):
        roll_value = sum( sorted(roll, reverse=True)[:Contest.BASE_DICE] )
        result[roll_value] += 1

    total = sum(result.values())
    return {
        roll_value : count / total
        for roll_value, count in result.items()
    }

# precalculate for all normal skill levels
if _PRECALC_TABLES:
    for level in SkillLevel:
        get_roll_table(level.bonus_dice)

@lru_cache
def get_opposed_roll_table(bonus_dice: int, opponent_dice: int) -> Mapping[int, float]:
    roll_table = get_roll_table(bonus_dice)
    oppo_table = get_roll_table(opponent_dice)

    result = Counter()
    for roll_value, roll_prob in roll_table.items():
        for oppo_value, oppo_prob in oppo_table.items():
            result[roll_value - oppo_value] += roll_prob * oppo_prob
    #print(sum(result.values()))
    return dict(result)

## Standard Contest Types

SKILL_ENDURANCE  = Contest('Endurance',  ['CON', 'CON'], innate=True)
SKILL_WILLPOWER  = Contest('Willpower',  ['POW', 'POW'], innate=True)
SKILL_PERCEPTION = Contest('Perception', ['INT', 'POW'], innate=True)
SKILL_EVADE      = Contest('Evade',      ['DEX', 'DEX'], innate=True)
SKILL_STEALTH    = Contest('Stealth',    ['DEX', 'INT'])
SKILL_RIDING     = Contest('Riding',     ['DEX', 'POW'])
SKILL_ACROBATICS = Contest('Acrobatics', ['STR', 'DEX'])

# not sure if these will be used
SKILL_BRAWN      = Contest('Brawn',      ['STR', 'SIZ'], innate=True)


## Combat Contest Types

class CombatTest(Contest):
    def get_attribute_modifier(self, protagonist: Creature) -> int:
        if protagonist.has_trait(FinesseTrait):
            return sum(
                max(protagonist.get_attribute(attr), protagonist.get_attribute(PrimaryAttribute.DEX))
                if attr == PrimaryAttribute.STR else protagonist.get_attribute(attr)
                for attr in self.key_attr
            )
        return super().get_attribute_modifier(protagonist)

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
