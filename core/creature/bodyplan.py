from __future__ import annotations

from enum import Enum, Flag, auto
from copy import copy as shallow_copy
from numbers import Number
from typing import TYPE_CHECKING, Iterable, Any, Union, Tuple, MutableMapping

if TYPE_CHECKING:
    from core.combat.unarmed import NaturalWeapon

class BodyElementType(Enum):
    HEAD = "head"
    UPPERBODY = "upper body"
    LOWERBODY = "lower body"
    LIMB = "limb"
    TAIL = "tail"

class BodyPartFlag(Flag):
    NONE = 0
    VITAL = auto()
    GRASP = auto()
    STANCE = auto()

# general rule of placement flags
class BodyElementPlacement(Flag):
    FORE    = auto()
    REAR    = auto()
    LEFT    = auto()
    RIGHT   = auto()
    CENTRAL = FORE|REAR
    MEDIAL  = LEFT|RIGHT
    DEFAULT = CENTRAL|MEDIAL

class BodyElement:
    def __init__(self,
                 id_tag: str,
                 elemtype: BodyElementType,
                 name: str = None,
                 placement: BodyElementPlacement = BodyElementPlacement.DEFAULT,
                 size: float = 1,
                 flags: BodyPartFlag = BodyPartFlag.NONE,
                 attacks: Iterable[NaturalWeapon] = (),
                 armor: float = 0):

        self.id_tag = id_tag
        self.type = elemtype
        self.name = name or id_tag
        self.placement = placement
        self.size = size
        self.flags = flags
        self.attacks = list(attacks)
        self.armor = armor

    def clone(self) -> BodyElement:
        result = shallow_copy(self)
        result.attacks = list(self.attacks)
        return result

class Morphology:
    SELECT_ALL = '*' # a special id tag used to select all BodyElements

    elements: MutableMapping[str, BodyElement]
    rel_size: MutableMapping[str, float]

    def __init__(self, elements: Iterable[BodyElement]):
        self.elements = { elem.id_tag : elem.clone() for elem in elements }
        self.update()

    def update(self) -> None:
        total_size = sum(bp.size for bp in self)
        self.rel_size = { bp.id_tag : bp.size/total_size for bp in self }

    def __iter__(self) -> Iterable[BodyElement]:
        return iter(self.elements.values())

    def __contains__(self, item: Union[BodyElement, str]):
        if isinstance(item, str):
            return item in self.elements.keys()
        return item in self.elements.values()

    def get_bodypart_ids(self) -> Iterable[str]:
        return iter(self.elements.keys())

    def get_bodypart(self, id_tag: str) -> BodyElement:
        return self.elements[id_tag]

    def get_relative_size(self, id_tag: str) -> float:
        return self.rel_size[id_tag]

    def get_proportions(self) -> Iterable[Tuple[str, float]]:
        return iter(self.rel_size.items())

    def clone(self) -> Morphology:
        return Morphology(self)

    def select(self, *id_tags: str) -> MorphologySelection:
        if self.SELECT_ALL in id_tags:
            selected = self.elements.values()
        else:
            selected = (self.elements[id_tag] for id_tag in id_tags)
        return MorphologySelection(self, selected)

    def add(self, elem: BodyElement) -> Morphology:
        self.elements[elem.id_tag] = elem
        self.update()
        return self

    def remove(self, id_tag: str) -> Morphology:
        del self.elements[id_tag]
        self.update()
        return self

class MorphologySelection:
    def __init__(self, source: Morphology, selected: Iterable[BodyElement]):
        self.source = source  # a Morphology instance
        self.selected = list(selected)

    def set(self, **assignments: Any) -> MorphologySelection:
        for name, value in assignments.items():
            for elem in self.selected:
                setattr(elem, name, value)
        return self

    def adjust(self, **adjustments: Number) -> MorphologySelection:
        for name, adjust in adjustments.items():
            for elem in self.selected:
                value = getattr(elem, name) + adjust
                setattr(elem, name, value)
        return self

    def add_unarmed_attack(self, attack: NaturalWeapon) -> MorphologySelection:
        for elem in self.selected:
            elem.attacks.append(attack)
        return self

    def remove(self) -> MorphologySelection:
        for elem in self.selected:
            self.source.remove(elem.id_tag)
        return self

    def select(self, *args: Any) -> MorphologySelection:
        return self.source.select(*args)

    def finalize(self) -> Morphology:
        self.source.update()
        return self.source