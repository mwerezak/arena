from enum import Flag, auto
from typing import TYPE_CHECKING

from core.dice import dice

if TYPE_CHECKING:
    from core.creature import Creature
    from core.combat.melee import CombatResult

class CriticalUsage(Flag):
    Offensive = auto()
    Defensive = auto()
    Both = Offensive | Defensive

## Criticals modify the result of an attack or produce some special effect
class CriticalEffect:
    name: str
    usage: CriticalUsage

    def can_use(self, user: Creature, result: CombatResult) -> bool:
        return False

    def apply(self, user: Creature, result: CombatResult) -> None:
        pass

# Default Criticals - Anyone can use

# MaxDamageCritical - (offensive) deal max damage instead of rolling
class MaxDamageCritical(CriticalEffect):
    name = 'Max Damage'
    usage = CriticalUsage.Offensive

    def can_use(self, user: Creature, result: CombatResult) -> bool:
        return result.is_effective_hit() and result.damage.min() < result.damage.max()

    def apply(self, user: Creature, result: CombatResult) -> None:
        result.damage = dice(result.damage.max())

# HitLocationCritical - (offensive) attack hit location of choice instead of random
class HitLocationCritical(CriticalEffect):
    name = 'Choose Hit Location'
    usage = CriticalUsage.Offensive

    def __init__(self, hitloc: str):
        self.hitloc = hitloc

    def can_use(self, user: Creature, result: CombatResult) -> bool:
        return result.is_effective_hit() and result.hitloc != self.hitloc

    def apply(self, user: Creature, result: CombatResult) -> None:
        result.hitloc = self.hitloc

# SecondaryAttackCritical - (both) simultaneous attack with an offhand or natural weapon, do not roll for criticals

# ImproveParryCritical - (defensive) ignore weapon force difference for defence
class ImproveParryCritical(CriticalEffect):
    name = 'Improved Parry'
    usage = CriticalUsage.Defensive

    def can_use(self, user: Creature, result: CombatResult) -> bool:
        pass

# CounterAttackCritical - (defensive) make opponent lose AP, force an attack from user
# PressAttackCritical - (offensive) same as CounterAttackCritical, but on offence
# BreakGrappleCritical - (defensive) break out of grapple or entanglement for free
# CloseRangeCritical - (both) reduce melee combat separation to desired step w/o spending AP (max 4 steps)
# OpenRangeCritical - (defensive) increase melee combat separation to desired step w/o spending AP (max 4 steps)

# Criticals provided by certain weapons/attacks or situations

# KnockdownCritical - (offensive) knock target prone - also available when charging?
# QuickGetUpCritical - (defensive) get up from being prone w/o spending AP
# GripTargetCritical - (offensive) grapple target for free - only for certain natural weapons
# EntangleCritical - (both) use an entangling weapon

# ImpaleCritical - (offensive) certain ranged attacks can lodge projectiles in the target