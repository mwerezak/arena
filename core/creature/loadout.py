"""
Loadouts are used to randomize Creatures.

A loadout consists of several loadout sets. Each set consists of one or more loadout options.
When a loadout is applied to a Creature, each set is applied by picking a single option from the set and
applying it to the Creature.

Loadouts currently apply equipment and traits to a creature.
"""

import random
from typing import TYPE_CHECKING, Iterable, Iterator, Tuple, Optional, List, Union, Any
from core.equipment import Equipment
from core.creature.traits import CreatureTrait

if TYPE_CHECKING:
    from core.creature import Creature

LoadoutItem = Union[Equipment, CreatureTrait]
LoadoutGroup = Iterable[LoadoutItem]

class LoadoutChoice:
    """Picks from a collection of LoadoutItems-compatible collections"""
    def __init__(self, options: Iterable[Tuple[float, Any]]):
        self.options: List[Tuple[float, LoadoutGroup]] = []
        for weight, option in options:
            if option is None:
                option = ()
            elif not isinstance(option, Iterable):
                option = [ option ]
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
    def __init__(self, *groups: LoadoutGroup):
        self.loadout = list(groups)

    def apply_loadout(self, creature: 'Creature') -> None:
        for group in self.loadout:
            for item in group:
                if isinstance(item, Equipment):
                    creature.add_equipment(item)
                if isinstance(item, CreatureTrait):
                    creature.add_trait(item)
