from typing import Mapping, MutableMapping, Collection, Tuple, Optional, Iterable, Any, Union

from core.constants import MeleeRange, CreatureSize, PrimaryAttribute
from core.combat.attack import MeleeAttack, MeleeAttackInstance
from core.creature.combat import MeleeCombat
from core.creature.template import CreatureTemplate
from core.creature.bodyplan import Morphology, BodyElementSpecial
from core.equipment import Equipment
from core.equipment.weapon import Weapon
from core.equipment.armor import Armor
from core.contest import Contest, SkillLevel
from core.creature.traits import CreatureTrait, SkillTrait
from core.action import Entity

class Creature(Entity):
    health: float

    def __init__(self, template: CreatureTemplate):
        self.template = template
        self.name = template.name
        self.health = template.max_health

        self._traits: MutableMapping[Any, CreatureTrait] = {
            trait.key : trait for trait in template.get_traits()
        }

        self._mount: Optional['Creature'] = None
        self._melee_combat: MutableMapping['Creature', MeleeCombat] = {}

        self._unarmed_attacks: Collection[Tuple[str, MeleeAttack]] = [
            (bp_tag, natural_weapon.create_attack(template))
            for bp_tag, natural_weapon in template.get_natural_weapons()
        ]

        self._natural_armor: Mapping[str, float] = {
            bp_tag : armor for bp_tag, armor in template.get_natural_armor()
        }

        self._equipment = []
        template.loadout.apply_loadout(self)

        self._held_items: MutableMapping[str, Equipment] = {
            bp.id_tag : None for bp in template.bodyplan if BodyElementSpecial.GRASP in bp.specials
        }

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'

    def __str__(self) -> str:
        return self.name

    @property
    def size(self) -> CreatureSize:
        return self.template.size

    @property
    def bodyplan(self) -> Morphology:
        return self.template.bodyplan

    def get_attribute(self, attr: Union[str, PrimaryAttribute]) -> int:
        return self.template.get_attribute(attr)

    def get_action_rate(self) -> float:
        return 1.0  # TODO

    def get_armor(self, bp_id: str) -> float:
        natural_armor = self._natural_armor.get(bp_id, 0)
        armor_values = (armor.armor_value.get(bp_id, 0) for armor in self._equipment if isinstance(armor, Armor))
        equipped_armor = max(armor_values, default = 0)
        return natural_armor + equipped_armor

    def get_encumbrance(self) -> float:
        result = 0.0

        armor_items = []
        for equipment in self._equipment:
            if isinstance(equipment, Armor):
                armor_items.append(equipment)
            else:
                result += getattr(equipment, 'encumbrance', 0.0)

        from_armor = { bp_tag : 0.0 for bp_tag in self.bodyplan.get_bodypart_ids() }
        for armor in armor_items:
            for bp_tag, enc in armor.encumbrance.items():
                from_armor[bp_tag] = max(from_armor[bp_tag], enc)
        return result + sum(from_armor.values())

    ## Traits

    def add_trait(self, trait: CreatureTrait) -> None:
        self._traits[trait.key] = trait

    def get_trait(self, key: Any) -> Optional[CreatureTrait]:
        return self._traits.get(key)

    def get_skill_level(self, contest: Contest) -> SkillLevel:
        trait: Optional[SkillTrait] = self.get_trait((SkillTrait, contest))
        if trait is not None:
            return trait.level
        return SkillLevel(0)

    ## Equipment

    def add_equipment(self, equipment: Equipment) -> None:
        if equipment not in self._equipment:
            self._equipment.append(equipment)

    def remove_equipment(self, equipment: Equipment) -> None:
        if equipment in self._equipment:
            self._equipment.remove(equipment)
        self.unequip_item(equipment)

    def get_equipment(self) -> Iterable[Equipment]:
        return iter(self._equipment)

    def try_equip_item(self, equipment: Equipment, *, use_hands: int = None) -> bool:
        self.unequip_item(equipment)

        req_hands = equipment.get_required_hands(self)
        if req_hands is None:
            return False

        empty_hands = list(self.get_empty_hands())

        min_hands, max_hands = req_hands
        if len(empty_hands) < min_hands:
            return False

        use_hands = (
            min(max(min_hands, use_hands), max_hands)
            if use_hands is not None else min_hands
        )

        self.add_equipment(equipment)
        for i in range(use_hands):
            self._held_items[empty_hands.pop()] = equipment
        return True

    def unequip_item(self, equipment: Equipment) -> None:
        for bp_tag, item in self._held_items.items():
            if item == equipment:
                self._held_items[bp_tag] = None

    def unequip_all(self) -> None:
        for bp_tag in self._held_items.keys():
            self._held_items[bp_tag] = None

    def get_held_items(self) -> Iterable[Equipment]:
        return iter(set(item for item in self._held_items.values() if item is not None))

    def get_item_held_by(self, equipment: Equipment) -> Iterable[str]:
        for bp_tag, item in self._held_items.items():
            if item == equipment:
                yield bp_tag

    def get_empty_hands(self) -> Iterable[str]:
        for bp_tag, item in self._held_items.items():
            if item is None and self.can_use_bodypart(bp_tag):
                yield bp_tag

    ## Melee Combat

    def can_use_bodypart(self, bp_tag: str) -> bool:
        return True  # stub

    def get_unarmed_attacks(self) -> Iterable[MeleeAttackInstance]:
        for bp_tag, attack in self._unarmed_attacks:
            if self.can_use_bodypart(bp_tag):
                yield attack.create_instance(self, 1)

    def get_held_item_attacks(self) -> Iterable[MeleeAttackInstance]:
        for item in self.get_held_items():
            if item.is_weapon():
                using_hands = sum(1 for bp_tag in self.get_item_held_by(item) if self.can_use_bodypart(bp_tag))
                yield from item.get_melee_attacks(self, using_hands)

    def get_melee_attacks(self) -> Iterable[MeleeAttackInstance]:
        yield from self.get_unarmed_attacks()
        yield from self.get_held_item_attacks()

    def get_melee_engage_distance(self) -> MeleeRange:
        attack_reach = (attack.max_reach for attack in self.get_melee_attacks())
        return max(attack_reach, default=MeleeRange(0))

    def get_melee_opponents(self) -> Iterable['Creature']:
        return iter(self._melee_combat.keys())

    def get_melee_combat(self, other: 'Creature') -> Optional[MeleeCombat]:
        return self._melee_combat.get(other, None)

    def add_melee_combat(self, other: 'Creature', melee: MeleeCombat) -> None:
        self._melee_combat[other] = melee

    def remove_melee_combat(self, other: 'Creature') -> None:
        if other in self._melee_combat:
            del self._melee_combat[other]
