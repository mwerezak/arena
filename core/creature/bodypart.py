from __future__ import annotations
from typing import TYPE_CHECKING, Iterable

from core.creature.bodyplan import BodyPartFlag

if TYPE_CHECKING:
    from core.creature import Creature
    from core.creature.bodyplan import BodyElement
    from core.combat.attack import MeleeAttack, MeleeAttackInstance

class BodyPart:
    def __init__(self, parent: Creature, template: BodyElement):
        self.parent = parent
        self.template = template

        self._unarmed_attacks = [
            natural_weapon.create_attack(parent.template)
            for natural_weapon in template.attacks
        ]

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self.parent}:{self.id_tag})>'

    @property
    def id_tag(self) -> str:
        return self.template.id_tag

    @property
    def flags(self) -> BodyPartFlag:
        return self.template.flags

    @property
    def exposure(self) -> float:
        return self.template.size

    @property
    def natural_armor(self) -> float:
        return self.template.armor

    def can_use(self) -> bool:
        return True  # todo

    def is_vital(self) -> bool:
        return BodyPartFlag.VITAL in self.flags

    def is_grasp_part(self) -> bool:
        return BodyPartFlag.GRASP in self.flags

    def is_stance_part(self) -> bool:
        return BodyPartFlag.STANCE in self.flags

    def get_unarmed_attacks(self) -> Iterable[MeleeAttackInstance]:
        for attack in self._unarmed_attacks:
            yield attack.create_instance(self.parent, 1)

    def get_armor(self) -> float:
        armor_values = (item.armor_value.get(self.id_tag, 0) for item in self.parent.inventory.get_armor_items())
        equipped_armor = max(armor_values, default = 0)
        return equipped_armor + self.natural_armor