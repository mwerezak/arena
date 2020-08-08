"""
Loadouts are used to randomize Creatures.

A loadout consists of several loadout sets. Each set consists of one or more loadout options.
When a loadout is applied to a Creature, each set is applied by picking a single option from the set and
applying it to the Creature.

Loadouts currently apply equipment and traits to a creature.
"""

import random
from enum import Enum
from typing import TYPE_CHECKING, Iterable, Iterator, NamedTuple, Tuple, Optional, Collection, List, Union, Any
from core.equipment import Equipment

if TYPE_CHECKING:
    from core.creature import Creature

class LoadoutHint(Enum):
    PrimaryWeapon = 'primary_weapon'
    SecondaryWeapon = 'secondary_weapon'
    BackupWeapon = 'backup_weapon'

class LoadoutItem(NamedTuple):
    equipment: Equipment
    hints: Collection[LoadoutHint] = ()

class LoadoutGroup:
    """Used to ensure an iterable of LoadoutItems"""
    def __init__(self, *contents: Union[Equipment, LoadoutItem]):
        self.contents: List[LoadoutItem] = []
        for item in contents:
            if not isinstance(item, LoadoutItem):
                item = LoadoutItem(item)
            self.contents.append(item)

    def __iter__(self) -> Iterator[LoadoutItem]:
        return iter(self.contents)

class LoadoutChoice:
    """Picks from a collection of LoadoutItems-compatible collections"""
    def __init__(self, options: Iterable[Tuple[float, Any]]):
        self.options: List[Tuple[float, LoadoutGroup]] = []
        for weight, option in options:
            if not isinstance(option, LoadoutGroup):
                if isinstance(option, Iterable):
                    option = LoadoutGroup(*option)
                else:
                    option = LoadoutGroup(option)
            self.options.append( (weight, option) )

    def choose_option(self) -> Optional[LoadoutGroup]:
        if len(self.options) > 0:
            weights, items = zip(*self.options)
            return random.choices(items, weights)[0]
        return None

    def __iter__(self) -> Iterator[LoadoutItem]:
        option = self.choose_option()
        return iter(option) or ()

class Loadout:
    def __init__(self, *groups: Iterable[LoadoutItem]):
        self.loadout = list(groups)

    def apply_loadout(self, creature: 'Creature') -> None:
        for group in self.loadout:
            for item in group:
                creature.add_equipment(item.equipment, item.hints)
