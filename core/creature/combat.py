from typing import TYPE_CHECKING, Tuple, Optional
from core.constants import MeleeRange
from core.creature.actions import Action, CreatureAction, DEFAULT_ACTION_WINDUP

if TYPE_CHECKING:
    from core.creature import Creature

def create_melee_combat(a: 'Creature', b: 'Creature') -> 'MeleeCombat':
    melee = MeleeCombat(a, b)
    a.add_melee_combat(b, melee)
    b.add_melee_combat(a, melee)
    return melee

class MeleeCombat:
    combatants: Tuple['Creature', 'Creature']
    separation: MeleeRange

    def __init__(self, a: 'Creature', b: 'Creature'):
        self.combatants = (a, b)
        self.separation = max(a.get_melee_engage_distance(), b.get_melee_engage_distance())

    def get_opponent(self, combatant: 'Creature') -> Optional['Creature']:
        if combatant == self.combatants[0]:
            return self.combatants[1]
        if combatant == self.combatants[1]:
            return self.combatants[0]
        return None

    def break_engagement(self) -> None:
        for i, j in [(0,1), (1,0)]:
            creature, opponent = self.combatants[i], self.combatants[j]
            creature.remove_melee_combat(opponent)

            action = creature.get_current_action()
            if getattr(action, 'attacker', None) is creature and getattr(action, 'defender', None) is opponent:
                creature.set_current_action(None)
        del self.combatants

class MeleeCombatAction(CreatureAction):
    def __init__(self, attacker: 'Creature', defender: 'Creature'):
        self.attacker = attacker
        self.defender = defender

    def get_base_windup(self) -> float:
        return DEFAULT_ACTION_WINDUP

    def can_resolve(self) -> bool:
        melee = self.attacker.get_melee_combat(self.defender)
        if melee is None:
            return False  # no longer engaged in melee combat
        if not any(attack.can_reach(melee.separation) for attack in self.attacker.get_melee_attacks()):
            return False  # attacker does not have any attacks that can reach
        return True

    def resolve(self) -> Optional[Action]:
        # Process interruptions
        # Choose attack
        # Resolve attack and defense rolls
        # Apply critical effects
        # Determine hit location
        # Apply damage
        pass

class AttackInterruptedAction(CreatureAction):
    """Used to take up the remaining time when a MeleeAttackActon is interrupted or resolved early
    due to a failed interruption attempt."""
    can_defend = False  # already attacked or defended

    def __init__(self, duration: float):
        self.duration = duration

    def get_base_windup(self) -> float:
        return self.duration

    def resolve(self) -> Optional[Action]:
        return None

## MeleeEngageAction - create a melee engagement between two creatures. Interrupts movement
## MeleeChargeAction - perform a melee charge, which can be done outside of engagement
## MeleeAttackAction - melee attack
## MeleeChangeRangeAction - change melee range (max 4)
## MeleeDisengageAction


## Passive actions... cannot normally be taken, but can be forced by other actions
## MeleeDefendAction - when interrupted by an attack
## OpportunityAttackAction - when opponent tries to change range ???
