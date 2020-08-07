
from enum import Enum, IntFlag
from copy import copy as shallow_copy
from numbers import Number
from typing import Iterable, Any, Union

class BodyElementType(Enum):
    HEAD = "head"
    UPPERBODY = "upper body"
    LOWERBODY = "lower body"
    LIMB = "limb"
    TAIL = "tail"

class BodyElementSpecial(Enum):
    VITAL = "vital"
    GRASP = "grasp"
    STANCE = "stance"

# general rule of placement flags
class BodyElementPlacement(IntFlag):
    FORE    = 0x1
    REAR    = 0x2
    LEFT    = 0x4
    RIGHT   = 0x8
    CENTRAL = FORE|REAR
    MEDIAL  = LEFT|RIGHT
    DEFAULT = CENTRAL|MEDIAL

class BodyElement:
    def __init__(self,
                 id_tag: str,
                 elemtype: BodyElementType,
                 name: str = None,
                 placement: BodyElementPlacement = BodyElementPlacement.DEFAULT,
                 exposure: float = 1.0,
                 specials: Iterable[BodyElementSpecial] = None):
        self.id_tag = id_tag
        self.type = elemtype
        self.name = name or id_tag
        self.placement = placement
        self.exposure = exposure
        self.specials = tuple(specials) if specials is not None else ()

    def clone(self) -> 'BodyElement':
        return shallow_copy(self)

class Morphology:
    SELECT_ALL = '*' # a special id tag used to select all BodyElements

    def __init__(self, elements: Iterable[BodyElement]):
        self.elements = { elem.id_tag : elem.clone() for elem in elements }
        self.update()

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

    def update(self) -> None:
        total_exposure = sum(elem.exposure for elem in self)
        for elem in self:
            elem.exposure /= total_exposure

    def clone(self) -> 'Morphology':
        return Morphology(self)

    def select(self, *id_tags: str) -> 'MorphologySelection':
        if self.SELECT_ALL in id_tags:
            selected = self.elements.values()
        else:
            selected = (self.elements[id_tag] for id_tag in id_tags)
        return MorphologySelection(self, selected)

    def add(self, elem: BodyElement) -> 'Morphology':
        self.elements[elem.id_tag] = elem
        self.update()
        return self

    def remove(self, id_tag: str) -> 'Morphology':
        del self.elements[id_tag]
        self.update()
        return self

class MorphologySelection:
    def __init__(self, source: Morphology, selected: Iterable[BodyElement]):
        self.source = source  # a Morphology instance
        self.selected = list(selected)

    def set(self, **assignments: Any) -> 'MorphologySelection':
        for name, value in assignments.items():
            for elem in self.selected:
                setattr(elem, name, value)
        return self

    def adjust(self, **adjustments: Number) -> 'MorphologySelection':
        for name, adjust in adjustments.items():
            for elem in self.selected:
                value = getattr(elem, name) + adjust
                setattr(elem, name, value)
        return self

    def remove(self) -> 'MorphologySelection':
        for elem in self.selected:
            self.source.remove(elem.id_tag)
        return self

    def select(self, *args: Any) -> 'MorphologySelection':
        return self.source.select(*args)

    def finalize(self) -> Morphology:
        self.source.update()
        return self.source