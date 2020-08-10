from typing import MutableMapping, Type, Union, Any, Optional, Iterable, Tuple

from core.creature.bodyplan import Morphology
from core.combat.unarmed import NaturalWeapon
from core.constants import PrimaryAttribute, SizeCategory
from core.creature.loadout import Loadout
from core.creature.traits import CreatureTrait

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
            self.loadout = loadout or Loadout()
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

