from __future__ import annotations

from enum import Flag, auto
from typing import TYPE_CHECKING, Optional

from core.dice import dice
from core.constants import Stance

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

    def __init__(self, user: Creature, result: MeleeCombatResolver, usage: CriticalUsage):
        self.user = user
        self.result = result
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

    def can_use(self) -> bool:
        return self.result.is_effective_hit() and self.result.damage.min() < self.result.damage.max()

    def apply(self) -> None:
        self.result.damage = dice(self.result.damage.max())

# HitLocationCritical - (offensive) attack hit location of choice instead of random
class HitLocationCritical(CriticalEffect):
    name = 'Choose Hit Location'
    usage = CriticalUsage.Offensive | CriticalUsage.Melee

    hitloc: Optional[BodyPart]

    def setup(self) -> None:
        attack = self.result.use_attack
        target = self.result.melee.get_opponent(self.user)
        hitlocs = {
            bp : bp.get_effective_damage(attack.damage.mean(), attack.armpen.mean())
            for bp in target.get_bodyparts()
        }
        self.hitloc = max(hitlocs.keys(), key=lambda k: hitlocs[k], default=None)

    def can_use(self) -> bool:
        return self.result.is_effective_hit() and self.result.hitloc != self.hitloc and self.hitloc is not None

    def apply(self) -> None:
        self.result.hitloc = self.hitloc

    def __str__(self) -> str:
        return f'{self.name}: {self.hitloc}'

# SecondaryAttackCritical - (both) simultaneous attack with an offhand or natural weapon, do not roll for criticals
class SecondaryAttackCritical(CriticalEffect):
    name = 'Secondary Attack'
    usage = CriticalUsage.General | CriticalUsage.Melee

    target: Creature
    attack: MeleeAttack

    def setup(self) -> None:
        ## TODO refactor shields to use a ShieldBlock object that has a source
        ## TODO prevent using natural attacks on BodyParts that are holding weapons
        used_attacks = [ self.result.use_attack, self.result.use_defence ]
        used_attacks.extend(secondary.use_attack for secondary in self.result.seconary_attacks)
        used_sources = [ attack.source for attack in used_attacks if attack is not None ]

        secondary_attacks = (
            attack for attack in self.user.get_melee_attacks()
            if attack.source not in used_sources and attack.can_attack(self.result.melee.separation)
        )

        self.target = self.result.melee.get_opponent(self.user)
        self.attack = self.user.tactics.get_secondary_attack(self.target, self.result.melee.separation, secondary_attacks)

    def can_use(self) -> bool:
        return not self.result.is_secondary and self.attack is not None and self.attack.can_attack(self.result.melee.separation)

    def apply(self) -> None:
        self.result.add_secondary_attack(self.user, self.target, self.attack)

    def __str__(self) -> str:
        return f'{self.name}: {self.attack.name}'

# ImproveParryCritical - (defensive) ignore weapon force difference for defence
class ImproveParryCritical(CriticalEffect):
    name = 'Improved Parry'
    usage = CriticalUsage.Defensive | CriticalUsage.Melee

    def can_use(self) -> bool:
        return not self.result.is_hit and self.result.damage_mult > 0

    def apply(self) -> None:
        self.result.damage_mult = 0

# CounterAttackCritical - (defensive) make opponent lose AP, force an attack from user
# PressAttackCritical - (offensive) same as CounterAttackCritical, but on offence

# CloseRangeCritical - (both) reduce melee combat separation to desired step w/o spending AP (max 4 steps)
class CloseRangeCritical(CriticalEffect):
    name = 'Close Distance'
    usage = CriticalUsage.General | CriticalUsage.Melee

    target_range: MeleeRange

    def setup(self) -> None:
        opponent = self.result.melee.get_opponent(self.user)
        desired_ranges = self.user.tactics.get_melee_range_priority(opponent)
        self.target_range = max(desired_ranges, key=lambda k: desired_ranges[k], default=None)

    def can_use(self) -> bool:
        return self.target_range is not None and self.target_range < self.result.melee.separation

    def apply(self) -> None:
        prev = self.result.melee.separation
        self.result.melee.separation = self.result.melee.get_range_shift(self.target_range)
        print(f'{self.user} closes distance with {self.result.melee.get_opponent(self.user)} ({prev} -> {self.result.melee.separation}).')

    def __str__(self) -> str:
        return f'{self.name}: {self.target_range}'

# OpenRangeCritical - (defensive) increase melee combat separation to desired step w/o spending AP (max 4 steps)
class OpenRangeCritical(CriticalEffect):
    name = 'Open Distance'
    usage = CriticalUsage.Defensive | CriticalUsage.Melee

    target_range: MeleeRange

    def setup(self) -> None:
        opponent = self.result.melee.get_opponent(self.user)
        desired_ranges = self.user.tactics.get_melee_range_priority(opponent)
        self.target_range = max(desired_ranges, key=lambda k: desired_ranges[k], default=None)

    def can_use(self) -> bool:
        return self.target_range is not None and self.target_range > self.result.melee.separation

    def apply(self) -> None:
        prev = self.result.melee.separation
        self.result.melee.separation = self.result.melee.get_range_shift(self.target_range)
        print(f'{self.user} opens distance with {self.result.melee.get_opponent(self.user)} ({prev} -> {self.result.melee.separation}).')

    def __str__(self) -> str:
        return f'{self.name}: {self.target_range}'

# Criticals provided by certain weapons/attacks or situations

# BreakGrappleCritical - (defensive) break out of grapple or entanglement for free

# QuickGetUpCritical - (defensive) get up from being prone w/o spending AP
class ChangeStanceCritical(CriticalEffect):
    name = 'Change Stance'
    usage = CriticalUsage.Defensive | CriticalUsage.Melee

    target_stance: Stance

    def setup(self) -> None:
        self.target_stance = self.user.get_max_stance()

    def can_use(self) -> bool:
        return self.user.stance.value < self.target_stance.value

    def apply(self) -> None:
        self.user.change_stance(self.target_stance)
        print(f'{self.user} {self._action_text[self.user.stance]}.')

    _action_text = {
        Stance.Standing : 'gets up',
        Stance.Crouched : 'crouches',
        Stance.Prone    : 'goes prone',
    }

    def __str__(self) -> str:
        return f'{self.name}: {self.target_stance}'


# GripTargetCritical - (offensive) grapple target for free - only for certain natural weapons
# EntangleCritical - (both) use an entangling weapon

# ImpaleCritical - (offensive) certain ranged attacks can lodge projectiles in the target

DEFAULT_CRITICALS = [
    MaxDamageCritical,
    HitLocationCritical,
    SecondaryAttackCritical,
    ImproveParryCritical,
    CloseRangeCritical,
    OpenRangeCritical,
    ChangeStanceCritical,
]