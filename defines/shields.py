from core.equipment.weapon import Weapon, ShieldBlock
from core.combat.attack import MeleeAttackTemplate
from core.combat.damage import DamageType
from core.combat.attacktraits import CannotDefendTrait
from core.contest import CombatSkillClass
from core.dice import dice
from core.constants import *

SHIELD_BUCKLER = Weapon(
    name = 'Buckler', size = SizeCategory.Tiny, skill_class = CombatSkillClass.Shield, encumbrance = 1, cost = 50,
    shield = ShieldBlock(block_reach = REACH_SHORT, block_force = FORCE_MEDIUM, block_bonus = -2, block_ranged = 15),
    melee_attacks= [
        MeleeAttackTemplate('Bash', (REACH_SHORT, REACH_SHORT), FORCE_TINY, DamageType.Bludgeon, dice(1, 3), -dice(1, 3), traits=[CannotDefendTrait()]),
    ]
)

SHIELD_SMALL = Weapon(
    name = 'Small Shield', size = SizeCategory.Small, skill_class = CombatSkillClass.Shield, encumbrance = 2, cost = 150,
    shield = ShieldBlock(block_reach = REACH_SHORT, block_force = FORCE_LARGE, block_bonus = -1, block_ranged = 30),
    melee_attacks= [
        MeleeAttackTemplate('Bash', (REACH_SHORT, REACH_SHORT), FORCE_SMALL, DamageType.Bludgeon, dice(1, 4), -dice(1, 3), traits=[CannotDefendTrait()]),
    ]
)

SHIELD_MEDIUM = Weapon(
    name = 'Medium Shield', size = SizeCategory.Medium, skill_class = CombatSkillClass.Shield, encumbrance = 3, cost = 300,
    shield = ShieldBlock(block_reach = REACH_SHORT, block_force = FORCE_OVERWM, block_bonus = 0, block_ranged = 45),
    melee_attacks= [
        MeleeAttackTemplate('Bash', (REACH_SHORT, REACH_SHORT), FORCE_SMALL, DamageType.Bludgeon, dice(1, 4), -dice(1, 3), traits=[CannotDefendTrait()]),
    ]
)

SHIELD_LARGE = Weapon(
    name = 'Large Shield', size = SizeCategory.Medium, skill_class = CombatSkillClass.Shield, encumbrance = 4, cost = 450,
    shield = ShieldBlock(block_reach = REACH_SHORT, block_force = FORCE_OVERWM, block_bonus = 1, block_ranged = 60),
    melee_attacks= [
        MeleeAttackTemplate('Bash', (REACH_SHORT, REACH_SHORT), FORCE_SMALL, DamageType.Bludgeon, dice(1, 4), -dice(1, 3), traits=[CannotDefendTrait()]),
    ]
)