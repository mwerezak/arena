from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Set, Tuple, Optional

if TYPE_CHECKING:
    from core.creature import Creature
    from core.creature.bodypart import BodyPart
    from core.equipment import Equipment

class Inventory:
    def __init__(self, parent: Creature, equip_slots: Iterable[BodyPart]):
        self.parent = parent
        self._contents: Set[Equipment] = set()
        self._slots = { bp : None for bp in equip_slots }

    def add(self, equipment: Equipment) -> None:
        self._contents.add(equipment)

    def remove(self, equipment: Equipment) -> None:
        self._contents.remove(equipment)
        self.unequip_item(equipment)

    def __iter__(self) -> Iterable[Equipment]:
        return iter(self._contents)

    def can_equip(self, equipment: Equipment) -> bool:
        req_hands = equipment.get_required_hands(self.parent)
        if req_hands is None:
            return False
        min_hands, max_hands = req_hands
        if min_hands > sum(1 for bp in self.get_equip_slots()):
            return False
        return True

    def try_equip_item(self, equipment: Equipment, *, use_hands: int = None) -> bool:
        self.unequip_item(equipment)

        if not self.can_equip(equipment):
            return False

        empty_hands = list(self.get_empty_slots())

        min_hands, max_hands = equipment.get_required_hands(self.parent)
        if len(empty_hands) < min_hands:
            return False

        use_hands = (
            min(max(min_hands, use_hands), max_hands)
            if use_hands is not None else min_hands
        )

        self.add(equipment)  # ensure that it's actually in our inventory
        for i in range(use_hands):
            self._slots[empty_hands.pop()] = equipment
        return True

    def unequip_item(self, equipment: Equipment) -> None:
        for bp, item in self._slots.items():
            if item == equipment:
                self._slots[bp] = None

    def unequip_all(self) -> None:
        for bp in self._slots.keys():
            self._slots[bp] = None

    def get_slot_equipment(self) -> Iterable[Tuple[BodyPart, Optional[Equipment]]]:
        return iter(self._slots.items())

    def get_held_items(self) -> Iterable[Equipment]:
        return iter(set(item for item in self._slots.values() if item is not None))

    def get_item_held_by(self, equipment: Equipment) -> Iterable[BodyPart]:
        for bp, item in self._slots.items():
            if item == equipment:
                yield bp

    def get_equip_slots(self) -> Iterable[BodyPart]:
        for bp, item in self._slots.items():
            if bp.can_use():
                yield bp

    def get_empty_slots(self) -> Iterable[BodyPart]:
        for bp, item in self._slots.items():
            if item is None and bp.can_use():
                yield bp

    def get_armor_items(self) -> Iterable[Equipment]:
        for item in self._contents:
            if item.is_armor():
                yield item

    def get_encumbrance_total(self) -> float:
        result = 0.0

        from_armor = {}
        for equipment in self._contents:
            if equipment.is_armor():
                for bp_tag, enc in equipment.encumbrance.items():
                    from_armor[bp_tag] = max(enc, from_armor.setdefault(bp_tag, 0))
            else:
                result += equipment.encumbrance

        return result + sum(from_armor.values())