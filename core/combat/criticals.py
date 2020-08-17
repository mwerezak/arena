from __future__ import annotations

import random
from enum import Flag, auto
from typing import TYPE_CHECKING, Optional

from core.dice import dice
from core.constants import Stance
from core.creature.actions import DisruptedAction
from core.contest import ContestResult, OpposedResult, DifficultyGrade, SKILL_ACROBATICS

if TYPE_CHECKING:
    from core.constants import MeleeRange
    from core.creature import Creature
    from core.creature.bodypart import BodyPart
    from core.combat.attack import MeleeAttack
    from core.combat.resolver import MeleeCombatResolver

class CriticalUsage(Flag):
    Offensive = auto()
    Defensive = auto()
    General = Offensive | Defensive
    Melee = auto()
    Ranged = auto()

## Criticals modify the result of an attack or produce some special effect
class CriticalEffect:
    name: str
    usage: CriticalUsage
    weight: float = 1.0

    def __init__(self, user: Creature, combat: MeleeCombatResolver, usage: CriticalUsage):
        self.user = user
        self.combat = combat
        self.usage = usage
        self.setup()

    def setup(self) -> None:
        pass

    def can_use(self) -> bool:
        return False

    def apply(self) -> None:
        pass

    def __str__(self) -> str:
        return self.name

# Default Criticals - Anyone can use

# MaxDamageCritical - (offensive) deal max damage instead of rolling
class MaxDamageCritical(CriticalEffect):
    name = 'Max Damage'
    usage = CriticalUsage.Offensive | CriticalUsage.Melee
    weight = 5

    def can_use(self) -> bool:
        return self.combat.is_effective_hit() and self.combat.damage.min() < self.combat.damage.max()

    def apply(self) -> None:
        self.combat.damage = dice(self.combat.damage.max())

# HitLocationCritical - (offensive) attack hit location of choice instead of random
class HitLocationCritical(CriticalEffect):
    name = 'Choose Hit Location'
    usage = CriticalUsage.Offensive | CriticalUsage.Melee
    weight = 4

    hitloc: Optional[BodyPart]

    def setup(self) -> None:
        attack = self.combat.use_attack
        target = self.combat.melee.get_opponent(self.user)
        hitlocs = {
            bp : bp.get_effective_damage(attack.damage.mean(), attack.armpen.mean())
            for bp in target.get_bodyparts()
        }
        self.hitloc = max(hitlocs.keys(), key=lambda k: (hitlocs[k], random.random()), default=None)

    def can_use(self) -> bool:
        return self.combat.is_effective_hit() and self.combat.hitloc != self.hitloc and self.hitloc is not None

    def apply(self) -> None:
        self.combat.hitloc = self.hitloc

    def __str__(self) -> str:
        return f'{self.name}: {self.hitloc}'

# SecondaryAttackCritical - (both) simultaneous attack with an offhand or natural weapon, do not roll for criticals
class SecondaryAttackCritical(CriticalEffect):
    name = 'Secondary Attack'
    usage = CriticalUsage.Offensive | CriticalUsage.Melee
    weight = 1

    target: Creature
    attack: MeleeAttack

    def setup(self) -> None:
        used_attacks = [self.combat.use_attack]
        used_attacks.extend(secondary.use_attack for secondary in self.combat.seconary_attacks)
        used_sources = [ attack.source for attack in used_attacks if attack is not None ]

        secondary_attacks = (
            attack for attack in self.user.get_melee_attacks()
            if attack.source not in used_sources and attack.can_attack(self.combat.melee.get_separation())
        )

        self.target = self.combat.melee.get_opponent(self.user)
        self.attack = self.user.tactics.get_secondary_attack(self.target, self.combat.melee.get_separation(), secondary_attacks)

    def can_use(self) -> bool:
        return not self.combat.is_secondary and self.attack is not None and self.attack.can_attack(self.combat.melee.get_separation())

    def apply(self) -> None:
        self.combat.add_secondary_attack(self.user, self.target, self.attack)

    def __str__(self) -> str:
        return f'{self.name}: {self.attack.name}'

# ImproveParryCritical - (defensive) ignore weapon force difference for defence
class ImproveParryCritical(CriticalEffect):
    name = 'Improved Parry'
    usage = CriticalUsage.Defensive | CriticalUsage.Melee
    weight = 2

    def can_use(self) -> bool:
        return self.combat.is_effective_hit()

    def apply(self) -> None:
        self.combat.damage_mult = 0

# DisruptCritical - (both) make opponent lose AP
class DisruptCritical(CriticalEffect):
    name = 'Disrupt Opponent'
    usage = CriticalUsage.General | CriticalUsage.Melee
    weight = 5

    def can_use(self) -> bool:
        opponent = self.combat.melee.get_opponent(self.user)
        action = opponent.get_current_action()
        return self.combat.melee.can_attack(self.user) and (action is None or action.force_next is None)

    def apply(self) -> None:
        opponent = self.combat.melee.get_opponent(self.user)
        action = opponent.get_current_action()
        if action is not None:
            action.set_force_next(DisruptedAction())
        else:
            opponent.set_current_action(DisruptedAction())

# PressAttackCritical - (offensive) same as CounterAttackCritical, but on offence


# CloseRangeCritical - (both) reduce melee combat separation to desired step w/o spending AP (max 4 steps)
class CloseRangeCritical(CriticalEffect):
    name = 'Close Distance'
    usage = CriticalUsage.General | CriticalUsage.Melee
    weight = 5

    target_range: MeleeRange

    def setup(self) -> None:
        opponent = self.combat.melee.get_opponent(self.user)
        self.target_range = self.user.tactics.get_desired_melee_range(opponent)

    def can_use(self) -> bool:
        return self.target_range is not None and self.target_range < self.combat.melee.get_separation()

    def apply(self) -> None:
        prev = self.combat.melee.get_separation()
        self.combat.melee.change_separation(self.target_range)
        print(f'{self.user} closes distance with {self.combat.melee.get_opponent(self.user)} ({prev} -> {self.combat.melee.get_separation()}).')

    def __str__(self) -> str:
        return f'{self.name}: {self.target_range}'

# OpenRangeCritical - (defensive) increase melee combat separation to desired step w/o spending AP (max 4 steps)
class OpenRangeCritical(CriticalEffect):
    name = 'Open Distance'
    usage = CriticalUsage.Defensive | CriticalUsage.Melee
    weight = 3

    target_range: MeleeRange

    def setup(self) -> None:
        opponent = self.combat.melee.get_opponent(self.user)
        self.target_range = self.user.tactics.get_desired_melee_range(opponent)

    def can_use(self) -> bool:
        return self.target_range is not None and self.target_range > self.combat.melee.get_separation()

    def apply(self) -> None:
        prev = self.combat.melee.get_separation()
        self.combat.melee.change_separation(self.target_range)
        print(f'{self.user} opens distance with {self.combat.melee.get_opponent(self.user)} ({prev} -> {self.combat.melee.get_separation()}).')

    def __str__(self) -> str:
        return f'{self.name}: {self.target_range}'

# Criticals provided by certain weapons/attacks or situations

# BreakGrappleCritical - (defensive) break out of grapple or entanglement for free

# QuickGetUpCritical - (defensive) get up from being prone w/o spending AP
class ChangeStanceCritical(CriticalEffect):
    name = 'Change Stance'
    usage = CriticalUsage.Defensive | CriticalUsage.Melee
    weight = 5

    target_stance: Stance

    def can_use(self) -> bool:
        return self.user.stance < self.user.max_stance

    def apply(self) -> None:
        self.user.change_stance(self.target_stance)
        print(f'{self.user} {self._action_text[self.user.stance]}.')

    _action_text = {
        Stance.Standing : 'stands up',
        Stance.Crouched : 'crouches',
        Stance.Prone    : 'goes prone',
    }

    def __str__(self) -> str:
        return f'{self.name}: {self.target_stance}'

# GripTargetCritical - (offensive) grapple target for free - only for certain natural weapons
# EntangleCritical - (both) use an entangling weapon

class KnockdownCritical(CriticalEffect):
    name = 'Knock Down'
    usage = CriticalUsage.Offensive | CriticalUsage.Melee
    weight = 3

    def can_use(self) -> bool:
        opponent = self.combat.melee.get_opponent(self.user)
        return opponent.stance > Stance.Prone and self.combat.is_effective_hit() and opponent.size <= self.user.size * 2

    def apply(self) -> None:
        opponent = self.combat.melee.get_opponent(self.user)
        modifier = opponent.get_resist_knockdown_modifier()
        acro_result = ContestResult(opponent, SKILL_ACROBATICS, modifier)
        knockdown_result = OpposedResult(self.combat.primary_result.pro_result, acro_result)
        print(knockdown_result.format_details())
        if knockdown_result.success:
            opponent.knock_down()

# ImpaleCritical - (offensive) certain ranged attacks can lodge projectiles in the target

DEFAULT_CRITICALS = [
    MaxDamageCritical,
    HitLocationCritical,
    SecondaryAttackCritical,
    ImproveParryCritical,
    DisruptCritical,
    CloseRangeCritical,
    OpenRangeCritical,
    ChangeStanceCritical,
]