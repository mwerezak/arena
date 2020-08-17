from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from core.action import Action
from core.constants import Stance

if TYPE_CHECKING:
    from core.creature import Creature
    from core.equipment import Equipment
    from core.action import Entity, ActionLoop

DEFAULT_ACTION_WINDUP = 100  # corresponds to 1 'action point' worth of time
SHORT_ACTION_WINDUP = int(DEFAULT_ACTION_WINDUP * (2/3)) + 1
LONG_ACTION_WINDUP = int(DEFAULT_ACTION_WINDUP * (4/3))

def can_interrupt_action(combatant: Creature) -> bool:
    action = combatant.get_current_action()
    if action is None:
        return True  # idle
    if isinstance(action, CreatureAction):
        return action.can_interrupt
    return False

class CreatureAction(Action):
    """Base class for all Actions performed by Creatures"""
    owner: Creature

    base_windup = DEFAULT_ACTION_WINDUP  # the base windup duration, adjusted by the creature's action rate

    # True if this Action can be interrupted to defend, otherwise being attacked leaves
    # the action's protagonist defenceless - generally True for anything that isn't a cooldown
    can_defend = True

    # True if this Action can be interrupted to perform attacks of opportunity or other actions
    can_interrupt = False

    def get_windup_duration(self) -> float:
        return self.base_windup / self.owner.get_action_rate()

    @property
    def protagonist(self) -> Creature:
        return self.owner

## DitherAction - the do nothing action
class DitherAction(CreatureAction):
    can_interrupt = True
    def __init__(self, duration: float):
        self.base_windup = duration  # duration in Time Units
    def resolve(self) -> Optional[Action]:
        return None  # does nothing

class DisruptedAction(CreatureAction):
    can_interrupt = False
    can_defend = True
    base_windup = LONG_ACTION_WINDUP

    def resolve(self) -> Optional[Action]:
        return None

class InterruptCooldownAction(CreatureAction):
    """Used when an action was interrupted to perform a different action immediately, paying the time cost afterwards
    instead of before. The elapsed time already payed for the action that was interrupted is credited to this one,
    reducing the total windup duration."""

    def __init__(self, interrupted: Optional[Action] = None):
        self.elaspsed_windup = interrupted.get_elapsed_windup() if interrupted is not None else 0

    def get_windup_duration(self) -> float:
        return max(self.base_windup / self.owner.get_action_rate() - self.elaspsed_windup, 0)

    def resolve(self) -> Optional[Action]:
        return None  # the action has already been performed

## DelayAction - check if a condition is met

class ChangeStanceAction(CreatureAction):
    base_windup = int(LONG_ACTION_WINDUP/2) # changing through two stance levels (e.g. Prone -> Standing) is a long action
    can_interrupt = False

    def __init__(self, target_stance: Stance):
        self.target_stance = target_stance

    @property
    def can_defend(self) -> bool:
        # not defending when getting up is actually good as otherwise the attacker can keep you down for a long time
        return self.target_stance < self.protagonist.stance

    def get_windup_duration(self) -> float:
        stance_change = self.target_stance.value - self.owner.stance.value
        return self.base_windup * max(stance_change, 1) / self.owner.get_action_rate()

    def can_resolve(self) -> bool:
        return self.owner.stance != self.target_stance

    def resolve(self) -> Optional[Action]:
        if self.owner.stance != self.target_stance:
            self.owner.change_stance(self.target_stance)
            print(f'{self.owner} {self._action_text[self.owner.stance]}.')
        return None

    _action_text = {
        Stance.Standing : 'gets up',
        Stance.Crouched : 'crouches',
        Stance.Prone    : 'goes prone',
    }

## Movement related actions...
## Mount/unmount
## figure out how stance (standing/crouching/prone) and movement speed (walk/run/sprint) are supposed to work

## Inventory related actions...

class SwitchHeldItemAction(CreatureAction):
    base_windup = SHORT_ACTION_WINDUP

    def __init__(self, equip_item: Optional[Equipment], *unequip_items: Equipment):
        self.equip_item = equip_item
        self.unequip_items = unequip_items

    def can_resolve(self) -> bool:
        if self.equip_item is None:
            return True  # unequipping only

        inventory = self.protagonist.inventory
        if self.equip_item in inventory.get_held_items():
            return False
        if self.equip_item not in inventory or not inventory.can_equip(self.equip_item):
            return False
        return True

    def resolve(self) -> Optional[Action]:
        inventory = self.protagonist.inventory

        for item in self.unequip_items:
            inventory.unequip_item(item)
            print(f'{self.protagonist} unequips {item}.')
        if self.equip_item is not None:
            min_hands, max_hands = self.equip_item.get_required_hands(self.protagonist)
            inventory.try_equip_item(self.equip_item, use_hands=max_hands)
            print(f'{self.protagonist} equips {self.equip_item}.')

        return None

## reload weapon