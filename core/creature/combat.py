from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Optional, Iterable

from core.constants import MeleeRange
from core.creature.actions import CreatureAction
from core.contest import ContestResult, OpposedResult, SKILL_EVADE
from core.combat.resolver import MeleeCombatResolver

if TYPE_CHECKING:
    from core.creature import Creature
    from core.creature.actions import Action

def join_melee_combat(a: Creature, b: Creature) -> MeleeCombat:
    melee = MeleeCombat(a, b)
    a.add_melee_combat(b, melee)
    b.add_melee_combat(a, melee)
    return melee

class MeleeCombat:
    MAX_RANGE_SHIFT = 4  # the max change allowed with a single action

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
        del self.combatants

    def get_range_shift(self, target_range: MeleeRange, max_shift: int = MAX_RANGE_SHIFT) -> MeleeRange:
        shift = min(abs(target_range - self.separation), max_shift)
        if target_range < self.separation:
            shift *= -1
        return self.separation.get_step(shift)

    def change_separation(self, value: MeleeRange) -> None:
        self.separation = value

def can_opportunity_attack(combatant: Creature):
    cur_action = combatant.get_current_action()
    if cur_action is None:
        return True  # idle
    return getattr(cur_action, 'can_attack', True)

class ChangeMeleeRangeAction(CreatureAction):
    can_attack = True

    def __init__(self, opponent: Creature, desired_range: MeleeRange):
        self.opponent = opponent
        self.desired_range = desired_range

    def get_opportunity_attack_ranges(self) -> Iterable[MeleeRange]:
        """Gets the ranges through which the target will pass"""
        melee = self.protagonist.get_melee_combat(self.opponent)
        final_separation = melee.get_range_shift(self.desired_range)
        min_range = min(melee.separation, final_separation)
        max_range = max(melee.separation, final_separation)
        return MeleeRange.range(min_range, max_range+1)

    def allow_opportunity_attack(self) -> bool:
        melee = self.opponent.get_melee_combat(self.protagonist)
        if self.desired_range >= melee.separation:
            return False  # can only opportunity attack when moving closer
        return can_opportunity_attack(self.opponent)

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

        success = True
        start_range = melee.separation
        final_range = melee.get_range_shift(self.desired_range)

        if contested_change:
            contest = OpposedResult(ContestResult(self.protagonist, SKILL_EVADE), ContestResult(self.opponent, SKILL_EVADE))
            print(contest.format_details())
            success = contest.success

        elif self.allow_opportunity_attack():
            # an attack of opportunity is allowed only if the change is not contested
            use_attack = self.opponent.tactics.get_opportunity_attack(self.protagonist, self.get_opportunity_attack_ranges())
            if use_attack is not None:
                attack_range = min(melee.separation, use_attack.max_reach)

                melee.change_separation(attack_range)
                combat = MeleeCombatResolver(self.opponent, self.protagonist)
                combat.resolve_melee_attack()

                melee.change_separation(final_range)
                combat.resolve_critical_effects()
                combat.resolve_damage()
                combat.resolve_seconary_attacks()

                if melee.separation != final_range:
                    success = False

        if success:
            melee.change_separation(final_range)
            print(f'{self.protagonist} {verb}s distance with {self.opponent} ({start_range} -> {melee.separation}).')

        return None

class MeleeCombatAction(CreatureAction):
    can_attack = True

    def __init__(self, target: Creature):
        self.defender = target

    def can_resolve(self) -> bool:
        melee = self.protagonist.get_melee_combat(self.defender)
        if melee is None:
            return False  # no longer engaged in melee combat
        if not any(attack.can_attack(melee.separation) for attack in self.protagonist.get_melee_attacks()):
            return False  # attacker does not have any attacks that can reach
        return True

    def resolve(self) -> Optional[Action]:
        # TODO Process interruptions

        # Choose attack
        # Resolve attack and defense rolls
        attack = MeleeCombatResolver(self.protagonist, self.defender)
        attack.resolve_melee_attack()

        # Apply critical effects, Apply damage
        attack.resolve_critical_effects()
        attack.resolve_damage()
        attack.resolve_seconary_attacks()

        return None

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


## MeleeEngageAction - create a melee engagement between two creatures. Interrupts movement
## MeleeChargeAction - perform a melee charge, which can be done outside of engagement
## MeleeAttackAction - melee attack
## MeleeChangeRangeAction - change melee range (max 4)
## MeleeDisengageAction


## Passive actions... cannot normally be taken, but can be forced by other actions
## MeleeDefendAction - when interrupted by an attack
## OpportunityAttackAction - when opponent tries to change range ???
