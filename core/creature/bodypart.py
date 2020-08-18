from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional

from core.creature.bodyplan import BodyPartFlag, BodyElementType
from core.contest import ContestResult

if TYPE_CHECKING:
    from core.creature import Creature
    from core.creature.bodyplan import BodyElement
    from core.combat.attack import MeleeAttack

class BodyPart:
    def __init__(self, parent: Creature, template: BodyElement):
        self.parent = parent
        self.template = template
        self.size = parent.bodyplan.get_relative_size(self.id_tag)
        self._injured = False

        self._unarmed_attacks = [
            natural_weapon.create_attack(parent.template)
            for natural_weapon in template.attacks
        ]

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self.parent}:{self.id_tag})>'

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self.template.name

    @property
    def id_tag(self) -> str:
        return self.template.id_tag

    @property
    def flags(self) -> BodyPartFlag:
        return self.template.flags

    @property
    def exposure(self) -> float:
        return self.size

    @property
    def natural_armor(self) -> float:
        return self.template.armor

    def can_use(self) -> bool:
        return not self._injured

    def is_vital(self) -> bool:
        return BodyPartFlag.VITAL in self.flags

    def is_grasp_part(self) -> bool:
        return BodyPartFlag.GRASP in self.flags

    def is_stance_part(self) -> bool:
        return BodyPartFlag.STANCE in self.flags

    def get_unarmed_attacks(self) -> Iterable[MeleeAttack]:
        for attack in self._unarmed_attacks:
            yield attack.create_instance(self.parent, 1, self)

    ## Armor and Damage

    def get_armor(self) -> float:
        armor_values = (item.armor_value.get(self.id_tag, 0) for item in self.parent.inventory.get_armor_items())
        equipped_armor = max(armor_values, default = 0)
        return max(equipped_armor, self.natural_armor, 0)

    def get_effective_damage(self, damage: float, armpen: float = 0) -> float:
        """Calculates the amount of health that would be lost if damage is applied to this BodyPart"""
        armor = self.get_armor()
        damage = max(damage - armor, min(armpen, damage))

        if not self.is_vital():
            damage /= 1.5
        elif self.template.type == BodyElementType.HEAD:
            damage *= 1.5
        return max(damage, 0)

    def apply_damage(self, damage: float, armpen: float = 0, attack_result: Optional[ContestResult] = None) -> float:
        if damage <= 0:
            return 0

        armor = self.get_armor()
        damage = max(damage - armor, min(armpen, damage))

        if damage > 3/2 * self.size * self.parent.max_health:
            print(f'{self.parent} suffers an injury to the {self}.')
            injury_result = self.parent.get_injury_result(attack_result)
            print(injury_result.format_details())
            if not injury_result.success:
                self.injure_part()

        wound = damage
        if not self.is_vital():
            wound /= 1.5
        elif self.template.type == BodyElementType.HEAD:
            wound *= 1.5

        if wound > 0:
            print(f'{self.parent} is wounded for {wound:.1f} damage (armour {armor}).')
            self.parent.apply_wounds(damage, attack_result)
        else:
            print(f'The armor absorbs the blow (armour {armor}).')
        print(f'{self.parent} health: {round(self.parent.health)}/{self.parent.max_health}')

        return wound

    def injure_part(self) -> None:
        self._injured = True
        if self.is_stance_part():
            self.parent.check_stance()
        if self.is_vital():
            self.parent.stun(can_defend=True)
        if self.is_grasp_part():
            held_items = (
                item for bp, item in self.parent.inventory.get_slot_equipment() if bp == self and item is not None
            )
            for item in held_items:
                self.parent.inventory.remove(item)
                print(f'{self.parent} drops the {item}.')

