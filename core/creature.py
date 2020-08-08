from typing import Union, MutableMapping, Tuple, Type, Optional, Iterable

from core.constants import PrimaryAttribute, CreatureSize, SizeCategory
from core.bodyplan import Morphology
from core.combat.attack import MeleeAttack
from core.traits import CreatureTrait

class Creature:
    health: float
    template: 'CreatureTemplate'
    # melee_combat: MutableMapping['Creature', 'MeleeCombat']
    # get_engage_range() -> MeleeRange

    # equipment
class CreatureTemplate:
    name: str

    def __init__(self, name: str = None, bodyplan: Morphology = None, *, template: 'CreatureTemplate' = None):
        if template is not None:
            self.name = template.name
            self.bodyplan = Morphology(template.bodyplan)
            self.attributes = dict(template.attributes)
            self.traits = dict(template.traits)
        else:
            self.bodyplan = bodyplan
            self.attributes: MutableMapping[PrimaryAttribute, int] = {attr : 0 for attr in PrimaryAttribute}
            self.traits: MutableMapping[Type[CreatureTrait], CreatureTrait] = {}
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
            self.traits[type(trait)] = trait
        return self

    def remove_trait(self, trait_type: Type[CreatureTrait]) -> 'CreatureTemplate':
        del self.traits[trait_type]
        return self

    def get_attribute(self, attr: Union[str, PrimaryAttribute]) -> int:
        if not isinstance(attr, PrimaryAttribute):
            attr = PrimaryAttribute[attr]
        return self.attributes[attr]

    def get_trait(self, trait_type: Type[CreatureTrait]) -> Optional[CreatureTrait]:
        return self.traits.get(trait_type)

    def get_traits(self) -> Iterable[CreatureTrait]:
        return iter(self.traits.values())

    def get_natural_armor(self) -> Iterable[Tuple[str, float]]:
        return ( (bp.id_tag, bp.armor) for bp in self.bodyplan )

    def get_unarmed_attacks(self) -> Iterable[Tuple[str, MeleeAttack]]:
        for bp in self.bodyplan:
            for unarmed in bp.unarmed:
                yield (bp.id_tag, unarmed.create_attack(self))

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

