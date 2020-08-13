
from typing import TYPE_CHECKING, Optional
from core.action import Action
if TYPE_CHECKING:
    from core.creature import Creature

DEFAULT_ACTION_WINDUP = 100  # corresponds to 1 'action point' worth of time

class CreatureAction(Action):
    """Base class for all Actions performed by Creatures"""
    owner: 'Creature'

    base_windup = DEFAULT_ACTION_WINDUP  # the base windup duration, adjusted by the creature's action rate

    can_defend = True  # True if this Action can be interrupted to defend, otherwise being attacked leaves the Creature defenceless
    can_attack = True  # True if this Action can be interrupted to perform attacks of opportunity

    def get_windup_duration(self) -> float:
        return self.base_windup / self.owner.get_action_rate()

## DitherAction - the do nothing action
class DitherAction(CreatureAction):
    def __init__(self, duration: float):
        self.base_windup = duration  # duration in Time Units
    def resolve(self) -> Optional[Action]:
        return None  # does nothing

## DelayAction - check if a condition is met

## These are just different names for DitherAction used for different purposes
## DisruptedAction
## EvadeAction



## Movement related actions...
## Mount/unmount
## figure out how stance (standing/crouching/prone) and movement speed (walk/run/sprint) are supposed to work

## Inventory related actions...
## Ready weapon
## reload weapon