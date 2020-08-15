from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from core.action import Action
from core.constants import Stance

if TYPE_CHECKING:
    from core.creature import Creature
    from core.action import Entity, ActionLoop

DEFAULT_ACTION_WINDUP = 100  # corresponds to 1 'action point' worth of time

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

# ## ForceNextAction - replace an action with a wrapper that resolves the wrapped action, then forces another action
# class ForceNextAction(CreatureAction):
#     def __init__(self, wrapped: CreatureAction, force_next: CreatureAction):
#         self.wrapped = wrapped
#         self.force_next = force_next
#         self.remaining_windup = wrapped.get_remaining_windup()
#         self.wrapped_active = wrapped.is_active()
#
#     @property
#     def can_defend(self) -> bool:
#         return self.wrapped.can_defend
#
#     @property
#     def can_interrupt(self) -> bool:
#         return self.wrapped.can_interrupt
#
#     def get_windup_duration(self) -> float:
#         return self.remaining_windup
#
#     def setup(self, owner: Entity, loop: ActionLoop) -> None:
#         if not self.wrapped_active:
#             self.wrapped.setup(owner, loop)
#
#
#
#     def can_resolve(self) -> bool:
#         return self.wrapped.can_resolve()
#
#     def resolve_failed(self) -> Optional[Action]:
#         next_action = self.wrapped.resolve_failed()
#
#         # if wrapped has a next action, use another ForceNextAction to make that action come after force_next
#         if next_action is not None:
#             return ForceNextAction(self.force_next, next_action)
#         return self.force_next
#
#     def resolve(self) -> Optional[Action]:
#         next_action = self.wrapped.resolve()
#

## DelayAction - check if a condition is met

class ChangeStanceAction(CreatureAction):
    base_windup = DEFAULT_ACTION_WINDUP/2

    def __init__(self, target_stance: Stance):
        self.target_stance = target_stance

    def get_windup_duration(self) -> float:
        stance_change = abs(self.owner.stance.value - self.target_stance.value)
        return self.base_windup * stance_change / self.owner.get_action_rate()

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
## Ready weapon
## reload weapon