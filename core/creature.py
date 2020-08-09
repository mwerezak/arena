from typing import Union, MutableMapping, Tuple, Type, Optional, Iterable, Any

from core.constants import PrimaryAttribute, SizeCategory, MeleeRange
from core.bodyplan import Morphology
from core.combat.attack import MeleeAttack
from core.combat.unarmed import NaturalWeapon
from core.combat.melee import MeleeCombat
from core.equipment import Equipment
from core.loadout import Loadout
from core.traits import CreatureTrait
from core.world.action import Entity, ActionLoop

class CreatureTemplate:
    def __init__(self,
                 name: str = None,
                 bodyplan: Morphology = None,
                 loadout: Loadout = None,
                 *, template: 'CreatureTemplate' = None):

        if template is not None:
            self.name = template.name
            self.bodyplan = Morphology(template.bodyplan)
            self.attributes = dict(template.attributes)
            self.traits = dict(template.traits)
            self.loadout = template.loadout
        else:
            self.bodyplan = bodyplan
            self.attributes: MutableMapping[PrimaryAttribute, int] = {attr : 0 for attr in PrimaryAttribute}
            self.traits: MutableMapping[Type[CreatureTrait], CreatureTrait] = {}
            self.loadout = loadout
        if name is not None:
            self.name = name

    @property
    def size(self) -> int:
        return self.get_attribute(PrimaryAttribute.SIZ) + SizeCategory.Medium.to_size()

    ## Creature Template Creation API

    def set_attributes(self, **attr_values: int) -> 'CreatureTemplate':
        for name, value in attr_values.items():
            attr = PrimaryAttribute[name]
            self.attributes[attr] = value
        return self

    def set_attribute(self, attr: Union[str, PrimaryAttribute], value: int) -> 'CreatureTemplate':
        if not isinstance(attr, PrimaryAttribute):
            attr = PrimaryAttribute[attr]
        self.attributes[attr] = value
        return self

    def modify_attributes(self, **attr_mods: int) -> 'CreatureTemplate':
        for name, mod in attr_mods.items():
            attr = PrimaryAttribute[name]
            self.attributes[attr] += mod
        return self

    def add_trait(self, *traits: CreatureTrait) -> 'CreatureTemplate':
        for trait in traits:
            self.traits[trait.key] = trait
        return self

    def remove_trait(self, key: Any) -> 'CreatureTemplate':
        del self.traits[key]
        return self

    def set_loadout(self, loadout: Loadout) -> 'CreatureTemplate':
        self.loadout = loadout
        return self

    def get_attribute(self, attr: Union[str, PrimaryAttribute]) -> int:
        if not isinstance(attr, PrimaryAttribute):
            attr = PrimaryAttribute[attr]
        return self.attributes[attr]

    def get_trait(self, key: Any) -> Optional[CreatureTrait]:
        return self.traits.get(key)

    def get_traits(self) -> Iterable[CreatureTrait]:
        return iter(self.traits.values())

    def get_natural_armor(self) -> Iterable[Tuple[str, float]]:
        return ( (bp.id_tag, bp.armor) for bp in self.bodyplan )

    def get_natural_weapons(self) -> Iterable[Tuple[str, NaturalWeapon]]:
        for bp in self.bodyplan:
            for unarmed in bp.attacks:
                yield bp.id_tag, unarmed

    @property
    def max_health(self) -> int:
        return self.size + self.get_attribute(PrimaryAttribute.CON)

    @property
    def initiative_bonus(self) -> int:
        return self.get_attribute(PrimaryAttribute.DEX) + self.get_attribute(PrimaryAttribute.INT)

    # OLD interrupt success
    # initiative = interrupting.owner.initiative - interrupted.owner.initiative
    # priority = interrupted.windup/interrupting.windup + (math.log(1.5) * initiative)
    # interrupt_chance = 1.0/(math.exp(-priority) + 1.0)

class Creature(Entity):
    mount: Optional['Creature']  # if this creature is riding on another creature
    melee_combat: MutableMapping['Creature', MeleeCombat]

    def __init__(self, template: CreatureTemplate, loop: ActionLoop):
        super().__init__(loop)

        self.template = template
        self.name = template.name
        self.health = template.max_health
        self.traits = { trait.key : trait for trait in template.get_traits() }

        self.mount = None
        self.melee_combat = {}

        self.unarmed_attacks = {
            (bp_tag, natural_weapon.create_attack(template))
            for bp_tag, natural_weapon in template.get_natural_weapons()
        }

        self.equipment = []
        template.loadout.apply_loadout(self)

    def add_trait(self, trait: CreatureTrait) -> None:
        self.traits[trait.key] = trait

    def add_equipment(self, equipment: Equipment) -> None:
        self.equipment.append(equipment)

    # health: float
    # template: CreatureTemplate
    # melee_combat: MutableMapping['Creature', 'MeleeCombat']
    # get_engage_range() -> MeleeRange
    # equipment

    # combat

    def can_use_unarmed_attacks(self, bp_tag: str) -> bool:
        return True

    def get_melee_attacks(self) -> Iterable[MeleeAttack]:
        for bp_tag, attack in self.unarmed_attacks:
            if self.can_use_unarmed_attacks(bp_tag):
                yield attack
        for item in self.equipment:
            if hasattr(item, 'get_melee_attacks'):
                yield from item.get_melee_attacks()

    def get_melee_engage_distance(self) -> MeleeRange:
        attack_reach = (attack.max_reach for attack in self.get_melee_attacks())
        return max(attack_reach, default=MeleeRange(0))

    def engage_melee_combat(self, other: 'Creature') -> MeleeCombat:
        melee = self.melee_combat.get(other, None)
        if melee is None:
            melee = MeleeCombat(self, other)
            self.melee_combat[other] = melee
            other.melee_combat[self] = melee
        return melee









