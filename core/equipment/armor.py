from enum import Enum
from typing import NamedTuple, Collection, Iterable

from core.creature import CreatureTemplate
from core.constants import SizeCategory
from core.equipment import Equipment

## Armor

# armor provides protection to the various hit locations based on it's layout
# while multiple pieces of armor can be worn, overlapping sections on the same
# bodypart/hitloc does not stack.

# armor is fitted for a particular Morphology. It can be worn by a creature with a
# different Morphology provided that each part is compatible.
# to be compatible the Morphology must have a bodypart with:
#   - the same body element type
#   - the same placement flags
#   - (% exposure) * creature size must be within X% of one the armor is fitted for

# used to determine which materials can be used for which armor types
class MaterialType(Enum):
    Mineral = 'mineral'  # hard brittle materials like obsidian, jade, or also bone, ivory, and shell
    Leather = 'leather'  # materials that can be flexible or cured to be hard and rigid
    Cloth = 'cloth'      # flexible materials
    Metal = 'metal'      # materials that are hard and rigid, yet ductile and formable

class ArmorMaterial(NamedTuple):
    name: str
    enc_mult: float
    cost_mult: float
    type: MaterialType

class ArmorType(NamedTuple):
    armor_value: int
    base_enc: float
    base_cost: float
    fit_thresh: float  # how closely the wearer must match the fit in order to equip
    allowed_materials: Collection[MaterialType]

class ArmorTemplate:
    def __init__(self, name: str, armor_type: ArmorType, material: ArmorMaterial, coverage: Iterable[str]):
        self.name = name
        self.armor_type = armor_type
        self.material = material
        self.coverage = list(coverage)

    def get_coverage(self) -> Iterable[str]:
        return iter(self.coverage)

    @property
    def base_cost(self) -> float:
        return self.armor_type.base_cost * self.material.cost_mult

    @property
    def base_encumbrance(self) -> float:
        return self.armor_type.base_enc * self.material.enc_mult

    @property
    def armor_value(self) -> float:
        return self.armor_type.armor_value

    def get_name(self) -> str:
        return self.material.name + ' ' + self.name

class Armor(Equipment):
    BASE_AREA = 0.15

    def __init__(self, template: ArmorTemplate, fitted_for: CreatureTemplate, name: str = None):
        self.name = name or template.get_name()
        self.template = template
        self.creature = fitted_for

        rel_sizes = dict(self.creature.bodyplan.get_proportions())
        coverage = [ bp_tag for bp_tag in self.template.get_coverage() if bp_tag in rel_sizes.keys() ]

        # noinspection PyTypeChecker
        size_mult = float(self.creature.size)/SizeCategory.Medium.to_size()
        self.cost = round(sum(
            self.template.base_cost * size_mult * rel_sizes[id_tag] / self.BASE_AREA for id_tag in coverage
        ))

        self.encumbrance = {
            id_tag : self.template.base_encumbrance * rel_sizes[id_tag] / self.BASE_AREA for id_tag in coverage
        }

        self.armor_value = {
            id_tag : self.template.armor_value for id_tag in coverage
        }
