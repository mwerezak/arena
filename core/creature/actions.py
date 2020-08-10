
from typing import Optional
from core.world.action import Action
from core.creature import Creature

DEFAULT_ACTION_WINDUP = 100

## DitherAction - the do nothing action
class DitherAction(Action):
    def __init__(self, duration: float):
        self.duration = duration  # duration in Time Units
    def get_base_windup(self) -> float:
        return self.duration
    def resolve(self) -> Optional[Action]:
        return None  # does nothing

## DelayAction - check if a condition is met

class MeleeCombatAction(Action):
    def __init__(self, attacker: Creature, defender: Creature):
        self.attacker = attacker
        self.defender = defender

    def get_base_windup(self) -> float:
        return DEFAULT_ACTION_WINDUP

    def can_resolve(self) -> bool:
        # are they still engaged in melee combat?
        return self.attacker.get_melee_combat(self.defender) is not None

    def resolve(self) -> Optional['Action']:
        # Process interruptions
        # Choose attack ???
        # Resolve attack and defense rolls
        # Apply critical effects
        # Determine hit location
        # Apply damage
        pass


## MeleeEngageAction - create a melee engagement between two creatures. Interrupts movement
## MeleeChargeAction - perform a melee charge, which can be done outside of engagement
## MeleeAttackAction - melee attack
## MeleeChangeRangeAction - change melee range (max 4)
## MeleeDisengageAction


## Passive actions... cannot normally be taken, but can be forced by other actions
## MeleeDefendAction - when interrupted by an attack
## OpportunityAttackAction - when opponent tries to change range ???

## These are just different names for DitherAction used for different purposes
## DisruptedAction
## EvadeAction



## Movement related actions...
## Mount/unmount
## figure out how stance (standing/crouching/prone) and movement speed (walk/run/sprint) are supposed to work

## Inventory related actions...
## Ready weapon
## reload weapon