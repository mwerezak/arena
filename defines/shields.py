from core.weapon import Weapon, ShieldBlock
from core.melee.attack import MeleeAttack, DamageType
from core.creature import SizeCategory
from core.dice import dice
from defines.constants import *

SHIELD_BUCKLER = Weapon(
    name = 'Buckler', size = SizeCategory.Small, encumbrance = 1, cost = 50,
    shield = ShieldBlock(block_force = FORCE_MEDIUM, block_bonus = 0, block_ranged = 15),
    melee = [
        MeleeAttack('Bash', (REACH_SHORT, REACH_SHORT), FORCE_TINY, DamageType.Bludgeon, dice(1,3), dice(0)),
    ]
)

SHIELD_SMALL = Weapon(
    name = 'Small Shield', size = SizeCategory.Small, encumbrance = 2, cost = 150,
    shield = ShieldBlock(block_force = FORCE_LARGE, block_bonus = 1, block_ranged = 30),
    melee = [
        MeleeAttack('Bash', (REACH_SHORT, REACH_SHORT), FORCE_SMALL, DamageType.Bludgeon, dice(1,4), dice(0)),
    ]
)

SHIELD_MEDIUM = Weapon(
    name = 'Medium Shield', size = SizeCategory.Medium, encumbrance = 3, cost = 300,
    shield = ShieldBlock(block_force = FORCE_OVERWM, block_bonus = 2, block_ranged = 45),
    melee = [
        MeleeAttack('Bash', (REACH_SHORT, REACH_SHORT), FORCE_SMALL, DamageType.Bludgeon, dice(1,4), dice(0)),
    ]
)

SHIELD_LARGE = Weapon(
    name = 'Large Shield', size = SizeCategory.Medium, encumbrance = 4, cost = 450,
    shield = ShieldBlock(block_force = FORCE_OVERWM, block_bonus = 3, block_ranged = 60),
    melee = [
        MeleeAttack('Bash', (REACH_SHORT, REACH_SHORT), FORCE_SMALL, DamageType.Bludgeon, dice(1,4), dice(0)),
    ]
)