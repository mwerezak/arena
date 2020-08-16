from __future__ import annotations
from typing import TYPE_CHECKING, Any

from core.equipment.template import EquipmentTemplate
from core.equipment.weapon import Weapon
from core.equipment.armor import Armor
if TYPE_CHECKING:
    from core.creature import Creature

class Equipment:
    def __init__(self, template: EquipmentTemplate, name: str = None):
        self.template = template
        self.name = name or template.name

    def __getattr__(self, name: str) -> Any:
        return getattr(self.template, name)

    def is_weapon(self) -> bool:
        return isinstance(self.template, Weapon)

    def is_armor(self) -> bool:
        return isinstance(self.template, Armor)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.template!r})'

    def __str__(self) -> str:
        return f'{self.template}'