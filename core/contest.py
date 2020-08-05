"""
Contests are various distinct categories under which creatures may be required to make differential or solo tests of
their ability. Each contest has two (not necessarily distinct) key PrimaryAttributes that contribute to the contest.
Creatures may also have traits that grant a certain level of expertise (valid levels 1-5) in a certain contest types.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Any, Iterable, Sequence
from core.creature import PrimaryAttribute

class Contest:
    def __init__(self, name: str, key_attr: Iterable[str]):
        self.name = name
        self.key_attr: Sequence[PrimaryAttribute] = tuple(PrimaryAttribute[s] for s in key_attr)

MELEE_COMBAT = Contest('melee',      ['STR', 'DEX'])
EVADE        = Contest('evade',      ['DEX', 'DEX'])
ENDURANCE    = Contest('endurance',  ['CON', 'CON'])
WILLPOWER    = Contest('willpower',  ['POW', 'POW'])
ATHLETICS    = Contest('athletics',  ['STR', 'SIZ'])
BRAWN        = Contest('brawn',      ['STR', 'SIZ'])
PERCEPTION   = Contest('perception', ['INT', 'POW'])
STEALTH      = Contest('stealth',    ['DEX', 'INT'])
