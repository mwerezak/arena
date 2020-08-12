from core.equipment.weapon import Weapon
from core.combat.attack import MeleeAttack
from core.combat.damage import DamageType
from core.contest import CombatSkillClass
from core.dice import dice
from core.constants import *

## Blades

WEAPON_BROADSWORD = Weapon(
    name = 'Broadsword', size = SizeCategory.Medium, skill_class = CombatSkillClass.Blade, encumbrance = 2, cost = 200,
    melee_attacks = [
        MeleeAttack('Slash',          (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Slashing, dice(1,8)),
        MeleeAttack('Thrust',         (REACH_LONG, REACH_MEDIUM),  FORCE_SMALL,  DamageType.Puncture, dice(1,6)),
        MeleeAttack('Pommel Strike',  (REACH_SHORT, REACH_CLOSE),  FORCE_SMALL,  DamageType.Bludgeon, dice(1,3), dice(0)),
    ],
)

WEAPON_LONGSWORD = Weapon(
    name = 'Longsword', size = SizeCategory.Medium, skill_class = CombatSkillClass.Blade, encumbrance = 2, cost = 250,
    melee_attacks = [
        MeleeAttack('Slash',          (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Slashing, dice(2,4)),
        MeleeAttack('Thrust',         (REACH_LONG, REACH_MEDIUM),  FORCE_MEDIUM, DamageType.Puncture, dice(1,6)),
        MeleeAttack('Pommel Strike',  (REACH_SHORT, REACH_CLOSE),  FORCE_SMALL,  DamageType.Bludgeon, dice(1,4), dice(0)),
    ],
)

WEAPON_GREATSWORD = Weapon(
    name = 'Greatsword', size = SizeCategory.Large, skill_class = CombatSkillClass.Blade, encumbrance = 4, cost = 300,
    melee_attacks = [
        MeleeAttack('Slash',          (REACH_MEDIUM, REACH_SHORT), FORCE_LARGE,  DamageType.Slashing, dice(2,6)),
        MeleeAttack('Thrust',         (REACH_LONG, REACH_MEDIUM),  FORCE_MEDIUM, DamageType.Puncture, dice(1,8)),
        MeleeAttack('Pommel Strike',  (REACH_SHORT, REACH_CLOSE),  FORCE_SMALL,  DamageType.Bludgeon, dice(1,4), dice(0)),
    ],
)

WEAPON_SCIMITAR = Weapon(
    name = 'Scimitar', size = SizeCategory.Medium, skill_class = CombatSkillClass.Blade, encumbrance = 2, cost = 175,
    melee_attacks = [
        MeleeAttack('Slash',          (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Slashing, dice(1,8)),
        MeleeAttack('Thrust',         (REACH_MEDIUM, REACH_SHORT), FORCE_SMALL,  DamageType.Puncture, dice(1,6)),
        MeleeAttack('Pommel Strike',  (REACH_SHORT, REACH_CLOSE),  FORCE_SMALL,  DamageType.Bludgeon, dice(1,4), dice(0)),
    ],
)

WEAPON_FALCHION = Weapon(
    name = 'Falchion', size = SizeCategory.Medium, skill_class = CombatSkillClass.Blade, encumbrance = 3, cost = 200,
    melee_attacks = [
        MeleeAttack('Hack',           (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Slashing, dice(1,8)+1),
        MeleeAttack('Pommel Strike',  (REACH_SHORT, REACH_CLOSE),  FORCE_SMALL,  DamageType.Bludgeon, dice(1,4), dice(0)),
    ],
)

WEAPON_SABRE = Weapon(
    name = 'Sabre', size = SizeCategory.Medium, skill_class = CombatSkillClass.Blade, encumbrance = 1, cost = 225,
    melee_attacks = [
        MeleeAttack('Slash',          (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Slashing, dice(1,6)+1),
        MeleeAttack('Thrust',         (REACH_MEDIUM, REACH_SHORT), FORCE_SMALL,  DamageType.Puncture, dice(1,6)),
        MeleeAttack('Pommel Strike',  (REACH_SHORT, REACH_CLOSE),  FORCE_SMALL,  DamageType.Bludgeon, dice(1,4), dice(0)),
    ],
)

WEAPON_SHORTSWORD = Weapon(
    name = 'Shortsword', size = SizeCategory.Small, skill_class = CombatSkillClass.Blade, encumbrance = 1, cost = 100,
    melee_attacks = [
        MeleeAttack('Stab',           (REACH_SHORT, REACH_CLOSE),  FORCE_MEDIUM, DamageType.Puncture, dice(1,8)),
        MeleeAttack('Slash',          (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Slashing, dice(1,6)),
        MeleeAttack('Thrust',         (REACH_MEDIUM, REACH_SHORT), FORCE_SMALL,  DamageType.Puncture, dice(1,4)),
        MeleeAttack('Pommel Strike',  (REACH_SHORT, REACH_CLOSE),  FORCE_SMALL,  DamageType.Bludgeon, dice(1,3), dice(0)),
    ],
)

WEAPON_DAGGER = Weapon(
    name = 'Dagger', size = SizeCategory.Tiny, skill_class = CombatSkillClass.Blade, encumbrance = 0, cost = 30,
    melee_attacks = [
        MeleeAttack('Stab',           (REACH_CLOSE, REACH_CLOSE), FORCE_MEDIUM, DamageType.Puncture, dice(1,6)),
        MeleeAttack('Slash',          (REACH_SHORT, REACH_CLOSE), FORCE_SMALL,  DamageType.Slashing, dice(1,4)),
        MeleeAttack('Thrust',         (REACH_SHORT, REACH_CLOSE), FORCE_SMALL,  DamageType.Puncture, dice(1,4)),
        MeleeAttack('Pommel Strike',  (REACH_CLOSE, REACH_CLOSE), FORCE_TINY,   DamageType.Bludgeon, dice(1,2), dice(0)),
    ],
    # Thrown Attack
)

WEAPON_KNIFE = Weapon(
    name = 'Knife', size = SizeCategory.Tiny, skill_class = CombatSkillClass.Blade, encumbrance = 0, cost = 10,
    melee_attacks = [
        MeleeAttack('Stab',           (REACH_CLOSE, REACH_CLOSE), FORCE_MEDIUM, DamageType.Puncture, dice(1,4)),
        MeleeAttack('Slash',          (REACH_SHORT, REACH_CLOSE), FORCE_SMALL,  DamageType.Slashing, dice(1,3)),
        MeleeAttack('Thrust',         (REACH_SHORT, REACH_CLOSE), FORCE_SMALL,  DamageType.Puncture, dice(1,3)),
        MeleeAttack('Pommel Strike',  (REACH_CLOSE, REACH_CLOSE), FORCE_TINY,   DamageType.Bludgeon, dice(1,2), dice(0)),
    ],
)

## Spears

WEAPON_SPEAR = Weapon(
    name = 'Spear', size = SizeCategory.Small, skill_class = CombatSkillClass.Polearm, encumbrance = 1, cost = 20,
    melee_attacks = [
        MeleeAttack('Stab',  (REACH_LONG, REACH_MEDIUM), FORCE_MEDIUM, DamageType.Puncture, dice(1,6)),
    ],
    # Thrown Attack
)

WEAPON_LONGSPEAR = Weapon(
    name = 'Longspear', size = SizeCategory.Medium, skill_class = CombatSkillClass.Polearm, encumbrance = 2, cost = 30,
    melee_attacks = [
        MeleeAttack('Stab',  (REACH_VLONG, REACH_LONG), FORCE_MEDIUM, DamageType.Puncture, dice(1,6)+1),
    ],
)

WEAPON_HALFSPEAR = Weapon(
    name = 'Halfspear', size = SizeCategory.Tiny, skill_class = CombatSkillClass.Polearm, encumbrance = 1, cost = 20,
    melee_attacks = [
        MeleeAttack('Stab',  (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Puncture, dice(1,6)),
    ],
    # Thrown Attack
)

WEAPON_PIKE = Weapon(
    name = 'Pike', size = SizeCategory.Large, skill_class = CombatSkillClass.Polearm, encumbrance = 3, cost = 90,
    melee_attacks = [
        MeleeAttack('Stab',  (REACH_EXTREME, REACH_VLONG), FORCE_LARGE, DamageType.Puncture, dice(1,8)+1),
    ],
)

## Axes

WEAPON_BATTLEAXE = Weapon(
    name = 'Battleaxe', size = SizeCategory.Medium, skill_class = CombatSkillClass.Axe, encumbrance = 1, cost = 100,
    melee_attacks = [
        MeleeAttack('Hack',          (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Slashing, dice(1,6)+1),
        MeleeAttack('Handle Strike', (REACH_CLOSE, REACH_CLOSE),  FORCE_SMALL,  DamageType.Bludgeon, dice(1,4), dice(0)),
    ],
)

WEAPON_HATCHET = Weapon(
    name = 'Hatchet', size = SizeCategory.Small, skill_class = CombatSkillClass.Axe, encumbrance = 1, cost = 25,
    melee_attacks = [
        MeleeAttack('Hack',          (REACH_SHORT, REACH_SHORT), FORCE_MEDIUM, DamageType.Slashing, dice(1,4)+1),
        MeleeAttack('Handle Strike', (REACH_SHORT, REACH_CLOSE), FORCE_SMALL,  DamageType.Bludgeon, dice(1,3), dice(0)),
    ],
    # Thrown Attack
)

WEAPON_GREATAXE = Weapon(
    name = 'Great Axe', size = SizeCategory.Large, skill_class = CombatSkillClass.Axe, encumbrance = 2, cost = 125,
    melee_attacks = [
        MeleeAttack('Hack',          (REACH_MEDIUM, REACH_SHORT), FORCE_LARGE, DamageType.Slashing, dice(1,10)+1),
        MeleeAttack('Handle Strike', (REACH_CLOSE, REACH_CLOSE),  FORCE_SMALL, DamageType.Bludgeon, dice(1,4), dice(0)),
    ],
)

WEAPON_HALBERD = Weapon(
    name = 'Halberd', size = SizeCategory.Large, skill_class = CombatSkillClass.Axe, encumbrance = 4, cost = 200,
    melee_attacks = [
        MeleeAttack('Stab',  (REACH_VLONG, REACH_LONG),  FORCE_MEDIUM, DamageType.Puncture, dice(1,6)+1, skill_class = CombatSkillClass.Polearm),
        MeleeAttack('Hack',  (REACH_LONG, REACH_MEDIUM), FORCE_LARGE,  DamageType.Slashing, dice(1,10)+1),
    ],
)

## Clubs/Maces

WEAPON_CLUB = Weapon(
    name = 'Club', size = SizeCategory.Small, skill_class = CombatSkillClass.Mace, encumbrance = 1, cost = 5,
    melee_attacks = [
        MeleeAttack('Strike', (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Bludgeon, dice(1,6), -dice(1,4)),
    ],
)

WEAPON_GREAT_CLUB = Weapon(
    name = 'Great Club', size = SizeCategory.Large, skill_class = CombatSkillClass.Mace, encumbrance = 3, cost = 50,
    melee_attacks = [
        MeleeAttack('Strike', (REACH_MEDIUM, REACH_SHORT), FORCE_LARGE, DamageType.Bludgeon, dice(1,10), dice(0)),
    ],
)

WEAPON_MACE = Weapon(
    name = 'Mace', size = SizeCategory.Small, skill_class = CombatSkillClass.Mace, encumbrance = 1, cost = 100,
    melee_attacks = [
        MeleeAttack('Strike', (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Bludgeon, dice(1,6), -dice(1)),
    ],
)

# a.k.a Military Pick
WEAPON_WARHAMMER = Weapon(
    name = 'Warhammer', size = SizeCategory.Medium, skill_class = CombatSkillClass.Mace, encumbrance = 3, cost = 180,
    melee_attacks = [
        MeleeAttack('Strike', (REACH_MEDIUM, REACH_SHORT), FORCE_MEDIUM, DamageType.Bludgeon, dice(1,8), dice(0)),
    ],
)

WEAPON_GREAT_HAMMER = Weapon(
    name = 'Great Hammer', size = SizeCategory.Large, skill_class = CombatSkillClass.Mace, encumbrance = 5, cost = 250,
    melee_attacks = [
        MeleeAttack('Strike', (REACH_LONG, REACH_MEDIUM), FORCE_LARGE, DamageType.Bludgeon, dice(1,10), dice(1)),
    ],
)

## Specialized/Species Weapon

WEAPON_MINOTAUR_AXE = Weapon(
    name = 'Minotaur Great Axe', size = SizeCategory.Huge, skill_class = CombatSkillClass.Axe, encumbrance = 4, cost = 200,
    melee_attacks = [
        MeleeAttack('Hack',          (REACH_LONG, REACH_MEDIUM), FORCE_OVERWM, DamageType.Slashing, dice(2,8)+1),
        MeleeAttack('Handle Strike', (REACH_SHORT, REACH_CLOSE), FORCE_MEDIUM, DamageType.Bludgeon, dice(1,6), dice(1)),
    ],
)