from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Optional, Iterable

from core.creature.actions import CreatureAction
from core.contest import ContestResult, OpposedResult, SKILL_EVADE
if TYPE_CHECKING:
    from core.constants import MeleeRange
    from core.creature import Creature
    from core.combat.attack import MeleeAttackInstance
    from core.creature.actions import Action

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

    def can_opportunity_attack(self, combatant: Creature):
        cur_action = combatant.get_current_action()
        if cur_action is None:
            return True  # idle
        return getattr(cur_action, 'can_attack', True)

class ChangeMeleeRangeAction(CreatureAction):
    MAX_RANGE_SHIFT = 4  # the max change allowed with a single action

    def __init__(self, protagonist: Creature, opponent: Creature, desired_range: MeleeRange):
        self.protagonist = protagonist
        self.opponent = opponent
        self.desired_range = desired_range

    def get_final_separation(self) -> MeleeRange:
        """Gets the final melee range if the action succeeds"""
        melee = self.protagonist.get_melee_combat(self.opponent)
        if melee is None: raise ValueError

        shift = min(abs(self.desired_range - melee.separation), self.MAX_RANGE_SHIFT)
        if self.desired_range < melee.separation:
            shift *= -1
        return melee.separation.get_step(shift)

    def get_opportunity_attack_ranges(self) -> Iterable[MeleeRange]:
        """Gets the ranges through which the target will pass"""
        melee = self.protagonist.get_melee_combat(self.opponent)
        if melee is None: raise ValueError

        final_separation = self.get_final_separation()
        min_range = min(melee.separation, final_separation)
        max_range = max(melee.separation, final_separation)
        return MeleeRange.range(min_range, max_range+1)

    def allow_opportunity_attack(self) -> bool:
        melee = self.opponent.get_melee_combat(self.protagonist)
        if self.desired_range >= melee.separation:
            return False  # can only opportunity attack when moving closer
        return melee.can_opportunity_attack(self.opponent)

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

        # determine opponent's reaction
        contested_change = self.opponent.tactics.choose_contest_change_range(self)

        # an attack of opportunity is allowed only if the change is not contested
        if not contested_change and self.allow_opportunity_attack():
            use_attack = self.opponent.tactics.get_opportunity_attack(self.protagonist, self.get_opportunity_attack_ranges())
            if use_attack is not None:
                print(f'Opportunity attack: {use_attack}')

        success = True
        if contested_change:
            contest = OpposedResult(ContestResult(self.protagonist, SKILL_EVADE), ContestResult(self.opponent, SKILL_EVADE))
            print(contest.format_details())
            success = contest.success

        if success:
            prev_range = melee.separation
            melee.separation = self.get_final_separation()
            print(f'{self.protagonist} {verb}s distance with {self.opponent} ({prev_range} -> {melee.separation}).')

        return None

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
