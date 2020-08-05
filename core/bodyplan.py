
from enum import Enum
from numbers import Number
from typing import NamedTuple, Iterable, Any, Collection

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

class BodyElement(NamedTuple):
    id_tag: str
    type: BodyElementType
    name: str = None
    exposure: float = 1.0
    specials: Collection[BodyElementSpecial] = None

    def clone(self) -> 'BodyElement':
        return BodyElement(*self)

class Morphology:
    SELECT_ALL = '*' # a special id tag used to select all BodyElements

    def __init__(self, elements: Iterable[BodyElement]):
        self.elements = { elem.id_tag : elem.clone() for elem in elements }

    def __getitem__(self, id_tag: str) -> BodyElement:
        return self.elements[id_tag]

    def __iter__(self) -> Iterable[BodyElement]:
        return iter(self.elements.values())

    def clone(self) -> 'Morphology':
        return Morphology(self)

    def select(self, *id_tags: str) -> 'MorphologySelection':
        if self.SELECT_ALL in id_tags:
            selected = self.elements.values()
        else:
            selected = (self.elements[id_tag] for id_tag in id_tags)
        return MorphologySelection(self, selected)

    def add(self, *elements: BodyElement) -> 'Morphology':
        for elem in elements:
            self.elements[elem.id_tag] = elem
        return self

    def remove(self, id_tag: str) -> 'Morphology':
        del self.elements[id_tag]
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

    def get_bodyplan(self) -> Morphology:
        return self.source

    def select(self, *args: Any) -> 'MorphologySelection':
        return self.source.select(*args)
