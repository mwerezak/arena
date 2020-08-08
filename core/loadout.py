"""
Loadouts are used to randomize Creatures.

A loadout consists of several loadout sets. Each set consists of one or more loadout options.
When a loadout is applied to a Creature, each set is applied by picking a single option from the set and
applying it to the Creature.

Loadouts currently apply equipment and traits to a creature.
"""

import random
from enum import Enum
from typing import Iterable, NamedTuple, Tuple, Optional, Collection
from core.equipment import Equipment
from core.creature import Creature

class LoadoutHint(Enum):
    PrimaryWeapon = 'primary_weapon'
    SecondaryWeapon = 'secondary_weapon'
    BackupWeapon = 'backup_weapon'

class LoadoutItem(NamedTuple):
    equipment: Equipment
    hints: Collection[LoadoutHint] = ()

LoadoutOption = Collection[LoadoutItem]
LoadoutSet = Collection[Tuple[float, LoadoutOption]]

class Loadout:
    def __init__(self, loadout: Iterable[LoadoutSet]):
        self.loadout = list(loadout)

    def __iter__(self) -> Iterable[LoadoutSet]:
        return iter(self.loadout)

    def apply_loadout(self, creature: Creature) -> None:
        for loadout_set in self.loadout:
            item = self.resolve_set(loadout_set)
            if item is not None:
                self.apply_item(item, creature)

    @staticmethod
    def resolve_set(loadout_set: LoadoutSet) -> Optional[LoadoutOption]:
        if len(loadout_set) > 0:
            items, weights = zip(*loadout_set)
            return random.choices(items, weights)[0]
        return None

    @staticmethod
    def apply_item(option: LoadoutOption, creature: Creature) -> None:
        for item in option:
            creature.add_equipment(item.equipment, item.hints)
