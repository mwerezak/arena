from enum import Enum
from typing import Union, Mapping, MutableMapping, Tuple, Type, Optional, Iterable

from core.constants import CreatureSize
from core.bodyplan import Morphology
from core.combat.attack import MeleeAttack
from core.traits import CreatureTrait

class PrimaryAttribute(Enum):
    STR = 'strength'
    CON = 'constitution'
    DEX = 'dexterity'
    INT = 'intelligence'
    POW = 'power'
    CHA = 'charisma'

class Creature:
    health: float
    template: 'CreatureTemplate'
    # melee_combat: MutableMapping['Creature', 'MeleeCombat']
    # get_engage_range() -> MeleeRange

    # equipment
class CreatureTemplate:
    name: str

    def __init__(self, name: str = None, size: CreatureSize = None, bodyplan: Morphology = None, *, template: 'CreatureTemplate' = None):
        if template is not None:
            self.name = name or template.name
            self.bodyplan = Morphology(template.bodyplan)
            self.size = template.size
            self._attributes = dict(template._attributes)
            self._traits = dict(template._traits)
            self._natural_armor = dict(template._natural_armor)
            self._unarmed_attacks = dict(template._unarmed_attacks)
        else:
            self.name = name
            self.bodyplan = bodyplan
            self.size = size
            self._attributes: MutableMapping[PrimaryAttribute, int] = {attr : 0 for attr in PrimaryAttribute}
            self._traits: MutableMapping[Type[CreatureTrait], CreatureTrait] = {}
            self._natural_armor: MutableMapping[str, float] = {}
            self._unarmed_attacks = []

    def attributes(self, **attr_values: int) -> 'CreatureTemplate':
        for name, value in attr_values.items():
            attr = PrimaryAttribute[name]
            self._attributes[attr] = value
        return self

    def add_trait(self, trait: CreatureTrait) -> 'CreatureTemplate':
        self._traits[type(trait)] = trait
        return self

    def remove_trait(self, trait_type: Type[CreatureTrait]) -> 'CreatureTemplate':
        del self._traits[trait_type]
        return self

    def natural_armor(self, value: float = None, **part_values: float) -> 'CreatureTemplate':
        for id_tag in self.bodyplan.get_bodypart_ids():
            if id_tag in part_values:
                self._natural_armor[id_tag] = part_values[id_tag]
            elif value is not None:
                self._natural_armor[id_tag] = value
        return self

    def add_unarmed_attack(self, bodypart_id: str, attack: MeleeAttack) -> 'CreatureTemplate':
        self._unarmed_attacks.append( (bodypart_id, attack) )
        return self

    # remove unarmed attacks?

    def get_attribute(self, attr: Union[str, PrimaryAttribute]) -> int:
        if not isinstance(attr, PrimaryAttribute):
            attr = PrimaryAttribute[attr]
        return self._attributes[attr]

    def get_trait(self, trait_type: Type[CreatureTrait]) -> Optional[CreatureTrait]:
        return self._traits.get(trait_type)

    def get_traits(self) -> Iterable[CreatureTrait]:
        return iter(self._traits.values())

    def get_natural_armor(self) -> Mapping[str, float]:
        return self._natural_armor

    def get_unarmed_attacks(self) -> Iterable[Tuple[str, MeleeAttack]]:
        return iter(self._unarmed_attacks)

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

