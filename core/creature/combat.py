from __future__ import annotations
import random
from typing import TYPE_CHECKING, Tuple, Optional, Iterable

from core.dice import dice
from core.constants import MeleeRange
from core.contest import Contest
from core.creature.actions import CreatureAction, InterruptCooldownAction, can_interrupt_action
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

def resolve_opposed_initiative(a: Creature, b: Creature) -> Optional[Creature]:
    a_initiative = a.get_initiative_modifier()
    b_initiative = b.get_initiative_modifier()

    a_roll = dice(1,10).get_roll_result()
    b_roll = dice(1,10).get_roll_result()
    a_total = a_roll + a_initiative
    b_total = b_roll + b_initiative

    winner = None
    if a_total != b_total:
        winner = a if a_total > b_total else b
    elif round(a_initiative) != round(b_initiative):
        winner = a if a_initiative > b_initiative else b

    success_text = f'{winner} takes initiative!' if winner is not None else 'Tie!'
    print(
        f'[Initiative] {a} vs {b} RESULT: {a_roll}{a_initiative:+.0f}={a_total:.0f} vs '
        f'{b_roll}{b_initiative:+.0f}={b_total:.0f} {success_text}'
    )
    return winner

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

    def can_attack(self, combatant: Creature) -> bool:
        opponent = self.get_opponent(combatant)
        if opponent is None:
            return False
        return any(attack.can_attack(self.separation) for attack in combatant.get_melee_attacks())

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


## MeleeChangeRangeAction - change melee range (max 4)
class ChangeMeleeRangeAction(CreatureAction):
    can_interrupt = True

    def __init__(self, opponent: Creature, desired_range: MeleeRange):
        self.opponent = opponent
        self.target_range = desired_range

    def get_opportunity_attack_ranges(self) -> Iterable[MeleeRange]:
        """Gets the ranges through which the target will pass"""
        melee = self.protagonist.get_melee_combat(self.opponent)
        final_separation = melee.get_range_shift(self.target_range)
        min_range = min(melee.separation, final_separation)
        max_range = max(melee.separation, final_separation)
        return MeleeRange.range(min_range, max_range+1)

    def allow_opportunity_attack(self) -> bool:
        melee = self.opponent.get_melee_combat(self.protagonist)
        if self.target_range >= melee.separation:
            return False  # can only opportunity attack when moving closer
        return True

    def can_resolve(self) -> bool:
        melee = self.protagonist.get_melee_combat(self.opponent)
        if melee is None:
            return False  # no longer engaged in melee combat
        if melee.separation == self.target_range:
            return False  # nothing to do
        return True  # TODO check for movement impairment

    def resolve(self) -> Optional[Action]:
        melee = self.protagonist.get_melee_combat(self.opponent)

        verb = 'close' if self.target_range <= melee.separation else 'open'
        print(f'{self.protagonist} attempts to {verb} distance with {self.opponent} ({melee.separation} -> {self.target_range}).')

        # determine opponent's reaction
        reaction = None
        if can_interrupt_action(self.opponent):
            reaction = self.opponent.tactics.choose_contest_change_range(self)

        success = True
        start_range = melee.separation
        final_range = melee.get_range_shift(self.target_range)

        if reaction == 'attack':
            if not can_interrupt_action(self.opponent) or not self.allow_opportunity_attack():
                reaction = 'contest'

        if reaction == 'contest':
            # action = self.opponent.get_current_action()
            # self.opponent.set_current_action(ContestChangeMeleeRangeAction(action))

            contest = OpposedResult(ContestResult(self.protagonist, SKILL_EVADE), ContestResult(self.opponent, SKILL_EVADE))
            print(contest.format_details())
            success = contest.success

        elif reaction == 'attack':
            # an attack of opportunity is allowed only if the change is not contested
            use_attack = self.opponent.tactics.get_opportunity_attack(self.protagonist, self.get_opportunity_attack_ranges())
            if use_attack is not None:
                attack_ranges = (reach for reach in self.get_opportunity_attack_ranges() if use_attack.can_attack(reach))
                attack_range = max(attack_ranges, default=None)
                if attack_range is not None:
                    melee.change_separation(attack_range)
                    combat = MeleeCombatResolver(self.opponent, self.protagonist)
                    if combat.generate_attack_results(force_evade=True):
                        # interrupt their current action to make the opportunity attack
                        action = self.opponent.get_current_action()
                        attack_action = OpportunityAttackAction(action)
                        self.opponent.set_current_action(attack_action)

                        # resolve the outcome of the attack
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

# class ContestChangeMeleeRangeAction(InterruptCooldownAction):
#     can_interrupt = False
#     can_defend = True

class OpportunityAttackAction(InterruptCooldownAction):
    can_interrupt = False
    can_defend = False

## MeleeEngageAction - create a melee engagement between two creatures. Interrupts movement
## MeleeChargeAction - perform a melee charge, which can be done outside of engagement
## MeleeDisengageAction

## MeleeCombatAction - resolve an attack between two creatures (which one is attacking and which one is defending can vary)
class MeleeCombatAction(CreatureAction):
    can_interrupt = True
    can_defend = True  # special case: being attacked by the target of this action, handled below

    def __init__(self, target: Creature):
        self.target = target

    def can_resolve(self) -> bool:
        melee = self.protagonist.get_melee_combat(self.target)
        if melee is None:
            return False  # no longer engaged in melee combat
        if not melee.can_attack(self.protagonist):
            return False  # attacker does not have any attacks that can it can use
                          # since we are just cancelling this action, any incoming opposed attack will resolve normally
        return True

    def resolve(self) -> Optional[Action]:
        # Process interruptions
        other_action = self.target.get_current_action()  # any action currently being taken by the target?

        # target is idle, create a MeleeDefendAction
        if other_action is None:
            if self._resolve_attack(self.protagonist, self.target):
                defend_action = MeleeDefendAction()
                self.target.set_current_action(defend_action)

        # opposed attack actions!
        elif isinstance(other_action, MeleeCombatAction) and other_action.target == self.protagonist:
            initiative = resolve_opposed_initiative(self.protagonist, self.target)

            # simultaneous attacks!
            if initiative is None:
                self._resolve_simultaneous_attacks()

            # target is attacking us first!
            elif initiative == self.target and self._resolve_attack(self.target, self.protagonist):
                defend_action = MeleeAttackCooldownAction(other_action)
                self.target.set_current_action(defend_action)  # replace the now-resolve attack action with a cooldown
                # no need to create a MeleeDefendAction - this action is wasted

            # protagonist attacks first!
            elif initiative == self.protagonist:
                if self._resolve_attack(self.protagonist, self.target):
                    defend_action = MeleeDefendAction(other_action)
                    self.target.set_current_action(defend_action)  # interrupt target's action

        # interrupt target's action with a MeleeDefendAction
        elif isinstance(other_action, CreatureAction) and other_action.can_defend:
            if self._resolve_attack(self.protagonist, self.target):
                defend_action = MeleeDefendAction(other_action)
                self.target.set_current_action(defend_action)

        else:
            # target cannot defend!
            self._resolve_attack(self.protagonist, self.target, can_defend=False)

        return None

    # return True if an attack actually happened
    def _resolve_attack(self, attacker: Creature, defender: Creature, *, can_defend: bool = True) -> Optional[MeleeCombatResolver]:
        attack = MeleeCombatResolver(attacker, defender)
        if attack.generate_attack_results(force_defenceless = not can_defend):
            attack.resolve_critical_effects()
            attack.resolve_damage()
            attack.resolve_seconary_attacks()
            return attack
        return None

    def _resolve_simultaneous_attacks(self):
        pro_attack = MeleeCombatResolver(self.protagonist, self.target)
        ant_attack = MeleeCombatResolver(self.target, self.protagonist)
        attacks = [pro_attack, ant_attack]

        random.shuffle(attacks)
        has_result = { attack : attack.generate_attack_results(force_defenceless=True) for attack in attacks }

        pro_crit_level = pro_attack.attacker_crit + ant_attack.defender_crit
        ant_crit_level = pro_attack.defender_crit + ant_attack.attacker_crit

        pro_attack.attacker_crit = min(max(0, pro_crit_level - ant_crit_level), Contest.MAX_CRIT)
        pro_attack.defender_crit = 0

        ant_attack.attacker_crit = min(max(0, ant_crit_level - pro_crit_level), Contest.MAX_CRIT)
        ant_attack.defender_crit = 0

        random.shuffle(attacks)
        for attack in attacks:
            if has_result[attack]: attack.resolve_critical_effects()

        random.shuffle(attacks)
        for attack in attacks:
            if has_result[attack]: attack.resolve_damage()

        random.shuffle(attacks)
        for attack in attacks:
            if has_result[attack]: attack.resolve_seconary_attacks()

## MeleeDefendAction - when interrupted by an attack
class MeleeDefendAction(InterruptCooldownAction):
    can_interrupt = False
    can_defend = False  # already defended

    def resolve(self) -> Optional[Action]:
        print(f'{self.protagonist} defends.')
        return None

class MeleeAttackCooldownAction(InterruptCooldownAction):
    can_interrupt = False
    can_defend = False



