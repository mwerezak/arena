
from typing import Optional
from core.action import Action

DEFAULT_ACTION_WINDUP = 100

class CreatureAction(Action):
    """Base class for all Actions performed by Creatures"""
    can_defend = True  # True if this Action can be interrupted to defend, otherwise being attacked leaves the Creature defenceless

## DitherAction - the do nothing action
class DitherAction(CreatureAction):
    def __init__(self, duration: float):
        self.duration = duration  # duration in Time Units
    def get_base_windup(self) -> float:
        return self.duration
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