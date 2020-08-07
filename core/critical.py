from enum import IntFlag

class CriticalUsage(IntFlag):
    Offensive = 0x1
    Defensive = 0x2

## Criticals modify the result of an attack or produce some special effect
class CriticalEffect:
    name: str
    usage: CriticalUsage

    # can_use(self, user: Creature, target: Creature, combat: MeleeCombat) -> bool - if the special can be used
    # __init__()  - should take parameters needed to resolve the effect of the special in combat


# Default Criticals - Anyone can use

# MaxDamageCritical - (offensive) deal max damage instead of rolling
# HitLocationCritical - (offensive) attack hit location of choice instead of random
# SecondaryAttackCritical - (both) simultaneous attack with an offhand or natural weapon, do not roll for criticals
# ImproveParryCritical - (defensive) ignore weapon force difference for defence
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