from enum import Enum
from collections import defaultdict
from typing import NamedTuple, Mapping, Collection, Tuple, Iterable

from core.equipment import Equipment
from core.creature import CreatureTemplate, CreatureSize, SizeCategory
from core.bodyplan import BodyElement

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

class ArmorComponent:
    COVERAGE_AREA = 0.15

    id_tag: str
    bodypart: BodyElement
    size: CreatureSize
    type: ArmorType
    material: ArmorMaterial
    coverage: float

    def __init__(self, id_tag:str, creature: CreatureTemplate, armor_type: ArmorType, material: ArmorMaterial):
        self.id_tag = id_tag
        self.bodypart = creature.bodyplan.get_bodypart(id_tag)
        self.size = creature.size
        self.type = armor_type
        self.material = material

    @property
    def armor_value(self) -> int:
        return self.type.armor_value

    @property
    def encumbrance(self) -> float:
        return self.type.base_enc * self.material.enc_mult * self.coverage/self.COVERAGE_AREA

    @property
    def cost(self) -> float:
        size_mult = float(self.size)/SizeCategory.Medium.value
        return self.type.base_cost * self.material.cost_mult * size_mult * self.coverage/self.COVERAGE_AREA

    @property
    def coverage(self) -> float:
        return self.bodypart.exposure

class Armor(Equipment):
    creature: CreatureTemplate  # the type of creature this armor is fitted for
    layout: Mapping[str, ArmorComponent]

    def __init__(self, name: str, creature: CreatureTemplate, components: Iterable[Tuple[str, ArmorType, ArmorMaterial]]):
        self.creature = creature
        self.layout = {
            id_tag : ArmorComponent(id_tag, creature, armor_type, material)
            for id_tag, armor_type, material in components
            if material.type in armor_type.allowed_materials
        }
        self.name = self.__create_name(name)

    def __str__(self) -> str:
        return self.name

    def __create_name(self, base_name: str) -> str:
        total_coverage = self.get_coverage()
        composition = defaultdict(float)
        for component in self.get_components():
            composition[component.material] += component.coverage/total_coverage
        top = list(sorted(composition.keys(), key=lambda m: composition[m], reverse=True))

        if len(top) >= 2:
            pri, sec = top[:2]
            if composition[sec] >= composition[pri] * 0.5:
                materials = [ pri, sec ]
            else:
                materials = [ pri ]
        else:
            materials = [ top[0] ] if len(top) > 0 else []

        return ' and '.join(material.name for material in materials) + ' ' + base_name

    def get_components(self) -> Iterable[ArmorComponent]:
        return iter(self.layout.values())

    def get_bodypart_ids(self) -> Iterable[str]:
        return iter(self.layout.keys())

    @property
    def encumbrance(self) -> float:
        return sum(component.encumbrance for component in self.get_components())

    @property
    def cost(self) -> float:
        return sum(component.cost for component in self.get_components())

    def get_armor_values(self) -> Mapping[str, int]:
        return { id_tag : component.armor_value for id_tag, component in self.layout.items() }

    def get_coverage(self) -> float:
        return sum(component.coverage for component in self.get_components())