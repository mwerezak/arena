from enum import Flag, auto
from typing import TYPE_CHECKING

from core.dice import dice

from core.creature import Stance
if TYPE_CHECKING:
    from core.creature import Creature
    from core.combat.result import CombatResult

class CriticalUsage(Flag):
    Offensive = auto()
    Defensive = auto()
    Both = Offensive | Defensive

## Criticals modify the result of an attack or produce some special effect
class CriticalEffect:
    name: str
    usage: CriticalUsage

    def __init__(self, user: Creature, result: CombatResult):
        self.user = user
        self.result = result
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
    usage = CriticalUsage.Offensive

    def can_use(self) -> bool:
        return self.result.is_effective_hit() and self.result.damage.min() < self.result.damage.max()

    def apply(self) -> None:
        self.result.damage = dice(self.result.damage.max())

# HitLocationCritical - (offensive) attack hit location of choice instead of random
class HitLocationCritical(CriticalEffect):
    name = 'Choose Hit Location'
    usage = CriticalUsage.Offensive

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

# ImproveParryCritical - (defensive) ignore weapon force difference for defence
class ImproveParryCritical(CriticalEffect):
    name = 'Improved Parry'
    usage = CriticalUsage.Defensive

    def can_use(self) -> bool:
        return not self.result.is_hit and self.result.damage_mult > 0

    def apply(self) -> None:
        self.result.damage_mult = 0

# CounterAttackCritical - (defensive) make opponent lose AP, force an attack from user
# PressAttackCritical - (offensive) same as CounterAttackCritical, but on offence

# BreakGrappleCritical - (defensive) break out of grapple or entanglement for free

# CloseRangeCritical - (both) reduce melee combat separation to desired step w/o spending AP (max 4 steps)
class CloseRangeCritical(CriticalEffect):
    name = 'Close Distance'
    usage = CriticalUsage.Both

    def setup(self) -> None:
        opponent = self.result.melee.get_opponent(self.user)
        desired_ranges = self.user.tactics.get_melee_range_priority(opponent)
        self.target_range = max(desired_ranges, key=lambda k: desired_ranges[k], default=None)

    def can_use(self) -> bool:
        return self.target_range is not None and self.target_range > self.result.melee.separation

    def apply(self) -> None:
        prev = self.result.melee.separation
        self.result.melee.separation = self.result.melee.get_range_shift(self.target_range)
        print(f'{self.user} closes distance with {self.result.melee.get_opponent(self.user)} ({prev} -> {self.result.melee.separation}).')

    def __str__(self) -> str:
        return f'{self.name}: {self.target_range}'

# OpenRangeCritical - (defensive) increase melee combat separation to desired step w/o spending AP (max 4 steps)
class OpenRangeCritical(CriticalEffect):
    name = 'Open Distance'
    usage = CriticalUsage.Defensive

    def setup(self) -> None:
        opponent = self.result.melee.get_opponent(self.user)
        desired_ranges = self.user.tactics.get_melee_range_priority(opponent)
        self.target_range = max(desired_ranges, key=lambda k: desired_ranges[k], default=None)

    def can_use(self) -> bool:
        return self.target_range is not None and self.target_range < self.result.melee.separation

    def apply(self) -> None:
        prev = self.result.melee.separation
        self.result.melee.separation = self.result.melee.get_range_shift(self.target_range)
        print(f'{self.user} opens distance with {self.result.melee.get_opponent(self.user)} ({prev} -> {self.result.melee.separation}).')

    def __str__(self) -> str:
        return f'{self.name}: {self.target_range}'


# Criticals provided by certain weapons/attacks or situations

# QuickGetUpCritical - (defensive) get up from being prone w/o spending AP
class ChangeStanceCritical(CriticalEffect):
    name = 'Change Stance'
    usage = CriticalUsage.Defensive

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