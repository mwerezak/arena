from typing import TYPE_CHECKING, Tuple, Optional, Mapping

from core.constants import MeleeRange
from core.creature.actions import Action, CreatureAction, DEFAULT_ACTION_WINDUP
from core.combat.attack import MeleeAttackInstance
from core.combat.tactics import get_attack_priority_at_ranges
from core.contest import Contest, ContestResult, OpposedResult, SKILL_EVADE

if TYPE_CHECKING:
    from core.creature import Creature

# TODO customizable variability
def choose_attack(attack_priority: Mapping[MeleeAttackInstance, float]) -> MeleeAttackInstance:
    return max(attack_priority.keys(), key=lambda k: attack_priority[k], default=None)

def join_melee_combat(a: 'Creature', b: 'Creature') -> 'MeleeCombat':
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


class ChangeMeleeRangeAction(CreatureAction):
    MAX_RANGE_SHIFT = 4  # the max change allowed with a single action

    def __init__(self, protagonist: 'Creature', opponent: 'Creature', desired_range: MeleeRange):
        self.protagonist = protagonist
        self.opponent = opponent
        self.desired_range = desired_range

    def get_base_windup(self) -> float:
        return DEFAULT_ACTION_WINDUP

    def can_resolve(self) -> bool:
        melee = self.protagonist.get_melee_combat(self.opponent)
        if melee is None:
            return False  # no longer engaged in melee combat
        if melee.separation == self.desired_range:
            return False  # nothing to do
        return True  # TODO check for movement impairment

    def resolve(self) -> Optional[Action]:
        melee = self.protagonist.get_melee_combat(self.opponent)

        ## determine opponent's reaction
        opportunity_attack = None
        contested_change = True

        # if the opponent is also changing range and this change takes us closer to their desired range
        # they will not contest the range change. They may still get an attack of opportunity, however
        opp_action = self.opponent.get_current_action()
        if isinstance(opp_action, ChangeMeleeRangeAction):
            new_distance = abs(self.desired_range - opp_action.desired_range)
            cur_distance = abs(melee.separation - opp_action.desired_range)
            if new_distance < cur_distance:
                contested_change = False

        # if the defender can attack and the success chance to contest is too small then use opportunity attack
        attack = self.get_opportunity_attack(melee)
        if attack is not None and Contest.get_opposed_chance(self.protagonist, SKILL_EVADE, self.opponent) > 0.667:
            contested_change = False

        # an attack of opportunity is only allowed if the change is not contested
        if not contested_change:
            opportunity_attack = attack

        if opportunity_attack is not None:
            pass  # resolve attack

        self.resolve_range_change(melee, contested_change)
        return None

    def resolve_range_change(self, melee: MeleeCombat, contested_change: bool) -> bool:
        verb = 'close' if self.desired_range <= melee.separation else 'open'
        print(f'{self.protagonist} attempts to {verb} distance with {self.opponent} ({melee.separation} -> {self.desired_range}).')

        success = True
        if contested_change:
            contest = OpposedResult(ContestResult(self.protagonist, SKILL_EVADE), ContestResult(self.opponent, SKILL_EVADE))
            print(contest.format_details())
            success = contest.success

        if success:
            prev_range = melee.separation
            shift = min(abs(self.desired_range - melee.separation), self.MAX_RANGE_SHIFT)
            if melee.separation < self.desired_range:
                shift *= -1
            melee.separation = melee.separation.get_step(shift)
            print(f'{self.protagonist} {verb}s distance with {self.opponent} ({prev_range} -> {melee.separation}).')
            return True
        return False

    def get_opportunity_attack(self, melee: MeleeCombat) -> Optional[MeleeAttackInstance]:
        if self.desired_range >= melee.separation:
            return None  # can only opportunity attack when moving closer

        # check if there is any attack at any of the ranges that can reach
        attack_priority = get_attack_priority_at_ranges(
            self.opponent, self.protagonist, (self.desired_range, melee.separation), self.opponent.get_melee_attacks(),
        )
        return choose_attack(attack_priority)

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
