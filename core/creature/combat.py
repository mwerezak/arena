from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Optional, Mapping

from core.creature.actions import CreatureAction
from core.creature.tactics import get_melee_attack_priority_at_ranges
from core.contest import Contest, ContestResult, OpposedResult, SKILL_EVADE
if TYPE_CHECKING:
    from core.constants import MeleeRange
    from core.creature import Creature
    from core.combat.attack import MeleeAttackInstance
    from core.creature.actions import Action

# TODO customizable variability
def choose_attack(attack_priority: Mapping[MeleeAttackInstance, float]) -> MeleeAttackInstance:
    return max(attack_priority.keys(), key=lambda k: attack_priority[k], default=None)

def join_melee_combat(a: Creature, b: Creature) -> MeleeCombat:
    melee = MeleeCombat(a, b)
    a.add_melee_combat(b, melee)
    b.add_melee_combat(a, melee)
    return melee

class MeleeCombat:
    combatants: Tuple[Creature, Creature]
    separation: MeleeRange

    def __init__(self, a: Creature, b: Creature):
        self.combatants = (a, b)
        self.separation = max(a.get_melee_engage_distance(), b.get_melee_engage_distance())

    def get_opponent(self, combatant: Creature) -> Optional[Creature]:
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

    def __init__(self, protagonist: Creature, opponent: Creature, desired_range: MeleeRange):
        self.protagonist = protagonist
        self.opponent = opponent
        self.desired_range = desired_range

    def can_resolve(self) -> bool:
        melee = self.protagonist.get_melee_combat(self.opponent)
        if melee is None:
            return False  # no longer engaged in melee combat
        if melee.separation == self.desired_range:
            return False  # nothing to do
        return True  # TODO check for movement impairment

    def resolve(self) -> Optional[Action]:
        melee = self.protagonist.get_melee_combat(self.opponent)

        verb = 'close' if self.desired_range <= melee.separation else 'open'
        print(f'{self.protagonist} attempts to {verb} distance with {self.opponent} ({melee.separation} -> {self.desired_range}).')

        ## determine opponent's reaction
        contested_change = True

        # if the opponent is also changing range and this change takes us closer to their desired range
        # they will not contest the range change. They may still get an attack of opportunity, however
        oppo_action = self.opponent.get_current_action()
        if isinstance(oppo_action, ChangeMeleeRangeAction):
            new_distance = abs(self.desired_range - oppo_action.desired_range)
            cur_distance = abs(melee.separation - oppo_action.desired_range)
            if new_distance < cur_distance:
                contested_change = False

        # can the opponent interrupt their current action to perform an opportunity attack?
        opportunity_attack = None
        if oppo_action is None or oppo_action.can_attack:
            opportunity_attack = self.get_opportunity_attack(melee)

        # if the defender can attack and the success chance to contest is too small then use opportunity attack
        contest_success_chance = Contest.get_opposed_chance(self.protagonist, SKILL_EVADE, self.opponent)
        if opportunity_attack is not None and contest_success_chance > 0.667:
            contested_change = False

        # an attack of opportunity is only allowed if the change is not contested
        if not contested_change and opportunity_attack is not None:
            if oppo_action is None or oppo_action.can_attack:
                print(f'Opportunity attack: {opportunity_attack}')

        self.resolve_range_change(melee, contested_change)
        return None

    def resolve_range_change(self, melee: MeleeCombat, contested_change: bool) -> bool:
        success = True
        if contested_change:
            contest = OpposedResult(ContestResult(self.protagonist, SKILL_EVADE), ContestResult(self.opponent, SKILL_EVADE))
            print(contest.format_details())
            success = contest.success

        if success:
            prev_range = melee.separation
            shift = min(abs(self.desired_range - melee.separation), self.MAX_RANGE_SHIFT)
            if self.desired_range < melee.separation:
                shift *= -1
            melee.separation = melee.separation.get_step(shift)
            verb = 'closes' if self.desired_range <= melee.separation else 'opens'
            print(f'{self.protagonist} {verb} distance with {self.opponent} ({prev_range} -> {melee.separation}).')
            return True
        return False

    def get_opportunity_attack(self, melee: MeleeCombat) -> Optional[MeleeAttackInstance]:
        if self.desired_range >= melee.separation:
            return None  # can only opportunity attack when moving closer

        # check if there is any attack at any of the ranges that can reach
        attack_priority = get_melee_attack_priority_at_ranges(
            self.opponent, self.protagonist, (self.desired_range, melee.separation), self.opponent.get_melee_attacks(),
        )
        return choose_attack(attack_priority)

class MeleeCombatAction(CreatureAction):
    def __init__(self, attacker: Creature, defender: Creature):
        self.attacker = attacker
        self.defender = defender

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

class InterruptedAction(CreatureAction):
    def __init__(self, duration: float):
        self.duration = duration

    def get_windup_duration(self) -> float:
        return self.duration

    def resolve(self) -> Optional[Action]:
        return None

class AttackInterruptedAction(InterruptedAction):
    """Used to take up the remaining time when a MeleeAttackActon is interrupted or resolved early
    due to a failed interruption attempt."""
    can_defend = False  # already attacked or defended
    can_attack = False


## MeleeEngageAction - create a melee engagement between two creatures. Interrupts movement
## MeleeChargeAction - perform a melee charge, which can be done outside of engagement
## MeleeAttackAction - melee attack
## MeleeChangeRangeAction - change melee range (max 4)
## MeleeDisengageAction


## Passive actions... cannot normally be taken, but can be forced by other actions
## MeleeDefendAction - when interrupted by an attack
## OpportunityAttackAction - when opponent tries to change range ???
