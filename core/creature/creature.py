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
    mount: Optional['Creature']  # if this creature is riding on another creature
    melee_combat: MutableMapping['Creature', MeleeCombat]

    def __init__(self, template: CreatureTemplate):
        self.template = template
        self.name = template.name
        self.health = template.max_health
        self.traits = { trait.key : trait for trait in template.get_traits() }

        self.mount = None
        self.melee_combat = {}

        self.unarmed_attacks: Collection[Tuple[str, MeleeAttack]] = [
            (bp_tag, natural_weapon.create_attack(template))
            for bp_tag, natural_weapon in template.get_natural_weapons()
        ]

        self.natural_armor: Mapping[str, float] = {
            bp_tag : armor for bp_tag, armor in template.get_natural_armor()
        }

        self.equipment = []
        template.loadout.apply_loadout(self)

        self.held_items: MutableMapping[str, Equipment] = {
            bp.id_tag : None for bp in template.bodyplan if BodyElementSpecial.GRASP in bp.specials
        }

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'

    @property
    def size(self) -> CreatureSize:
        return self.template.size

    @property
    def bodyplan(self) -> Morphology:
        return self.template.bodyplan

    def get_attribute(self, attr: Union[str, PrimaryAttribute]) -> int:
        return self.template.get_attribute(attr)

    def get_armor(self, bp_id: str) -> float:
        natural_armor = self.natural_armor.get(bp_id, 0)
        equipped_armor = max(
            ( armor.armor_value.get(bp_id) for armor in self.equipment if isinstance(armor, Armor) ),
            default = 0
        )
        return natural_armor + equipped_armor

    def get_encumbrance(self) -> float:
        result = 0.0

        armor_items = []
        for equipment in self.equipment:
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
        self.traits[trait.key] = trait

    def get_trait(self, key: Any) -> Optional[CreatureTrait]:
        return self.traits.get(key)

    def get_skill_level(self, contest: Contest) -> SkillLevel:
        trait: Optional[SkillTrait] = self.get_trait((SkillTrait, contest))
        if trait is not None:
            return trait.level
        return SkillLevel(0)

    ## Equipment

    def add_equipment(self, equipment: Equipment) -> None:
        if equipment not in self.equipment:
            self.equipment.append(equipment)

    def remove_equipment(self, equipment: Equipment) -> None:
        if equipment in self.equipment:
            self.equipment.remove(equipment)
        self.unequip_item(equipment)

    def try_equip_item(self, equipment: Equipment, use_grip: int = None) -> bool:
        self.unequip_item(equipment)

        req_grip = equipment.get_required_grip(self)
        if req_grip is None:
            return False

        empty_hands = [
            bp_tag for bp_tag, item in self.held_items.items()
            if item is None and self.can_use_bodypart(bp_tag)
        ]

        min_grip, max_grip = req_grip
        if len(empty_hands) < min_grip:
            return False

        use_grip = min(max(min_grip, use_grip), max_grip)
        self.add_equipment(equipment)
        for i in range(use_grip):
            self.held_items[empty_hands.pop()] = equipment
        return True

    def unequip_item(self, equipment: Equipment) -> None:
        for bp_tag, item in self.held_items.items():
            if item == equipment:
                self.held_items[bp_tag] = None

    def unequip_all(self) -> None:
        for bp_tag in self.held_items.keys():
            self.held_items[bp_tag] = None

    def get_held_items(self) -> Iterable[Equipment]:
        return iter(set(self.held_items.values()))

    def get_item_held_by(self, equipment: Equipment) -> Iterable[str]:
        for bp_tag, item in self.held_items.items():
            if item == equipment:
                yield bp_tag

    ## Melee Combat

    def can_use_bodypart(self, bp_tag: str) -> bool:
        return True  # stub

    def get_melee_attacks(self) -> Iterable[MeleeAttackInstance]:
        for bp_tag, attack in self.unarmed_attacks:
            if self.can_use_bodypart(bp_tag):
                yield attack.create_instance(self)
        for item in self.get_held_items():
            if isinstance(item, Weapon):
                using_grip = sum(1 for bp_tag in self.get_item_held_by(item) if self.can_use_bodypart(bp_tag))
                for attack in item.get_melee_attacks():
                    yield attack.create_instance(self, using_grip)

    def get_melee_engage_distance(self) -> MeleeRange:
        attack_reach = (attack.max_reach for attack in self.get_melee_attacks())
        return max(attack_reach, default=MeleeRange(0))

    def get_melee_combat(self, other: 'Creature') -> Optional[MeleeCombat]:
        return self.melee_combat.get(other, None)

    def add_melee_combat(self, other: 'Creature', melee: MeleeCombat) -> None:
        self.melee_combat[other] = melee

    def remove_melee_combat(self, other: 'Creature') -> None:
        if other in self.melee_combat:
            del self.melee_combat[other]
