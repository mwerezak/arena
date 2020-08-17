from core.creature.template import CreatureTemplate
from core.creature.loadout import Loadout, LoadoutChoice
from core.creature.traits import EvadeTrait, FinesseTrait
from core.equipment.armor import ArmorTemplate, Armor
from defines.species import SPECIES_GOBLIN, SPECIES_OGRE, SPECIES_ORC
from defines.armor import (
    ARMORTYPE_HIDE, ARMORTYPE_PADDED, ARMORTYPE_LAMINATED, ARMORTYPE_SCALED, MATERIAL_LEATHER, MATERIAL_IRON,
    PATTERN_CUIRASS, PATTERN_ARMOR, PATTERN_HAUBERK, PATTERN_HELMET,
)
from defines.weapons import (
    WEAPON_SPEAR, WEAPON_LONGSPEAR, WEAPON_DAGGER, WEAPON_SHORTSWORD, WEAPON_CLUB, WEAPON_MACE, WEAPON_GREAT_CLUB,
    WEAPON_BATTLEAXE, WEAPON_FALCHION,
)
from defines.shields import SHIELD_SMALL, SHIELD_MEDIUM, SHIELD_BUCKLER
from defines.traits import *

## Armor Templates

LEATHER_CUIRASS    = ArmorTemplate('Cuirass', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_CUIRASS)
LEATHER_ARMOR      = ArmorTemplate('Armor', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_ARMOR)

HIDE_CUIRASS = ArmorTemplate('Hide Cuirass', ARMORTYPE_HIDE, MATERIAL_LEATHER, PATTERN_CUIRASS)
HIDE_ARMOR = ArmorTemplate('Hide Armor', ARMORTYPE_HIDE, MATERIAL_LEATHER, PATTERN_ARMOR)

IRON_HELMET = ArmorTemplate('Helmet', ARMORTYPE_SCALED, MATERIAL_IRON, PATTERN_HELMET)
IRON_BRIGANDINE_CUIRASS = ArmorTemplate('Brigandine Cuirass', ARMORTYPE_SCALED, MATERIAL_IRON, PATTERN_CUIRASS)
IRON_BRIGANDINE_HAUBERK = ArmorTemplate('Brigandine Hauberk', ARMORTYPE_SCALED, MATERIAL_IRON, PATTERN_HAUBERK)

LEATHER_CAP    = ArmorTemplate('Cap', ARMORTYPE_PADDED, MATERIAL_LEATHER, PATTERN_HELMET)
LEATHER_HELMET = ArmorTemplate('Helmet', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_HELMET)

## Creature Templates

CREATURE_GOBLIN_SLAVE_SPEARMAN = (
    CreatureTemplate('Goblin Slave Spearman', template=SPECIES_GOBLIN)
    .set_loadout(Loadout(
        LoadoutChoice([
            (3, WEAPON_SPEAR),
            (3, [WEAPON_SPEAR, SHIELD_SMALL]),
            (2, WEAPON_LONGSPEAR),
            (1, [WEAPON_CLUB, SHIELD_SMALL]),
            (1, WEAPON_CLUB),
        ])
    ))
)

## Slave Slingers

CREATURE_GOBLIN_SPEARMAN = (
    CreatureTemplate('Goblin Spearman', template=SPECIES_GOBLIN)
    .add_trait(SkillTrait(SKILL_POLEARM, SkillLevel(1)))
    .set_loadout(Loadout(
        LoadoutChoice([
            (2, [WEAPON_LONGSPEAR, WEAPON_DAGGER, SkillTrait(SKILL_BLADE, SkillLevel(1))]),
            (1, [WEAPON_SPEAR, SHIELD_SMALL, SkillTrait(SKILL_SHIELD, SkillLevel(1))]),
            (1, [WEAPON_SPEAR, SHIELD_MEDIUM, SkillTrait(SKILL_SHIELD, SkillLevel(1))]),
        ]),
        LoadoutChoice([
            (3, Armor(LEATHER_HELMET, SPECIES_GOBLIN)),
            (5, Armor(LEATHER_CAP, SPECIES_GOBLIN)),
            (2, None),
        ]),
        LoadoutChoice([
            (3, Armor(HIDE_ARMOR, SPECIES_GOBLIN)),
            (5, Armor(LEATHER_CUIRASS, SPECIES_GOBLIN)),
            (2, Armor(LEATHER_ARMOR, SPECIES_GOBLIN)),
        ]),
    ))
)

CREATURE_GOBLIN_INFANTRY = (
    CreatureTemplate('Goblin Infantry', template=SPECIES_GOBLIN)
    .add_trait(
        SkillTrait(SKILL_MACE, SkillLevel(1)),
        SkillTrait(SKILL_SHIELD, SkillLevel(1)),
    )
    .set_loadout(Loadout(
        LoadoutChoice([(3, WEAPON_MACE), (1, WEAPON_CLUB)]),
        LoadoutChoice([(1, SHIELD_SMALL), (1, SHIELD_MEDIUM)]),
        LoadoutChoice([
            (3, Armor(LEATHER_HELMET, SPECIES_GOBLIN)),
            (5, Armor(LEATHER_CAP, SPECIES_GOBLIN)),
            (2, None),
        ]),
        LoadoutChoice([
            (3, Armor(HIDE_ARMOR, SPECIES_GOBLIN)),
            (5, Armor(LEATHER_CUIRASS, SPECIES_GOBLIN)),
            (2, Armor(LEATHER_ARMOR, SPECIES_GOBLIN)),
        ]),
    ))
)

CREATURE_GOBLIN_ENFORCER = (
    CreatureTemplate('Goblin Enforcer', template=SPECIES_GOBLIN)
    .modify_attributes(DEX=+1)
    .add_trait(
        SkillTrait(SKILL_ENDURANCE, SkillLevel(1)),
        SkillTrait(SKILL_UNARMED, SkillLevel(2)),
        SkillTrait(SKILL_EVADE, SkillLevel(2)),
        EvadeTrait(),
    )
    .set_loadout(Loadout(
        LoadoutChoice([
            (1, [WEAPON_SHORTSWORD, WEAPON_SHORTSWORD, SkillTrait(SKILL_BLADE, SkillLevel(2)), FinesseTrait]),
            (2, [WEAPON_SHORTSWORD, WEAPON_DAGGER, SkillTrait(SKILL_BLADE, SkillLevel(2)), FinesseTrait]),
            (1, [WEAPON_MACE, SHIELD_SMALL, SkillTrait(SKILL_MACE, SkillLevel(2)), SkillTrait(SKILL_SHIELD, SkillLevel(1))]),
        ]),
        LoadoutChoice([(1, Armor(HIDE_ARMOR, SPECIES_GOBLIN)), (1, None)]),
        LoadoutChoice([(1, Armor(IRON_HELMET, SPECIES_GOBLIN)), (1, Armor(LEATHER_HELMET, SPECIES_GOBLIN))]),
        LoadoutChoice([(5, Armor(LEATHER_CUIRASS, SPECIES_GOBLIN)), (3, Armor(IRON_BRIGANDINE_CUIRASS, SPECIES_GOBLIN)), (2, None)]),
    ))
)

CREATURE_GOBLIN_BOAR_RIDER = (
    CreatureTemplate('Goblin Boar Rider', template=SPECIES_GOBLIN)
    .modify_attributes(CON=+1)
    .add_trait(
        SkillTrait(SKILL_POLEARM, SkillLevel(2)),
        SkillTrait(SKILL_BLADE, SkillLevel(1)),
        SkillTrait(SKILL_RIDING, SkillLevel(2)),
        SkillTrait(SKILL_UNARMED, SkillLevel(1)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(1)),
    )
    .set_loadout(Loadout(
        [WEAPON_LONGSPEAR],
        LoadoutChoice([(1, WEAPON_SHORTSWORD), (1, WEAPON_DAGGER)]),
        LoadoutChoice([(1, SHIELD_SMALL), (1, SHIELD_MEDIUM)]),
        LoadoutChoice([
            (3, Armor(LEATHER_HELMET, SPECIES_GOBLIN)),
            (5, Armor(LEATHER_CAP, SPECIES_GOBLIN)),
            (2, None),
        ]),
        LoadoutChoice([
            (3, Armor(HIDE_ARMOR, SPECIES_GOBLIN)),
            (5, Armor(LEATHER_CUIRASS, SPECIES_GOBLIN)),
            (2, Armor(LEATHER_ARMOR, SPECIES_GOBLIN)),
        ]),
    ))
)

CREATURE_OGRE_BRUTE = (
    CreatureTemplate('Ogre Brute', template=SPECIES_OGRE)
    .add_trait(
        SkillTrait(SKILL_MACE, SkillLevel(3)),
        SkillTrait(SKILL_UNARMED, SkillLevel(3)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(3)),
    )
    .set_loadout(Loadout(
        [WEAPON_GREAT_CLUB],
        LoadoutChoice([
            (3, Armor(HIDE_ARMOR, SPECIES_OGRE)),
            (3, Armor(HIDE_CUIRASS, SPECIES_OGRE)),
            (4, None),
        ])
    ))
)

CREATURE_ORC_BARBARIAN = (
    CreatureTemplate('Orc Barbarian', template=SPECIES_ORC)
    .add_trait(
        SkillTrait(SKILL_SHIELD, SkillLevel(2)),
        SkillTrait(SKILL_UNARMED, SkillLevel(2)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(2)),
    )
    .set_loadout(Loadout(
        LoadoutChoice([
            (1, [WEAPON_BATTLEAXE, SkillTrait(SKILL_AXE, SkillLevel(2))]),
            (1, [WEAPON_FALCHION, SkillTrait(SKILL_BLADE, SkillLevel(2))]),
            (1, [WEAPON_MACE, SkillTrait(SKILL_MACE, SkillLevel(2))]),
        ]),
        LoadoutChoice([(1, SHIELD_SMALL), (1, SHIELD_MEDIUM)]),
        LoadoutChoice([
            (3, Armor(IRON_HELMET, SPECIES_ORC)),
            (5, Armor(LEATHER_HELMET, SPECIES_ORC)),
            (3, None),
        ]),
        LoadoutChoice([
            (1, Armor(HIDE_ARMOR, SPECIES_ORC)),
            (1, Armor(LEATHER_ARMOR, SPECIES_ORC)),
        ]),
        LoadoutChoice([
            (3, Armor(IRON_BRIGANDINE_HAUBERK, SPECIES_ORC)),
            (5, Armor(IRON_BRIGANDINE_CUIRASS, SPECIES_ORC)),
            (2, None),
        ])
    ))
)

## Orc Archer
CREATURE_ORC_ARCHER = (
    CreatureTemplate('Orc Archer', template=SPECIES_ORC)
    .add_trait(
        SkillTrait(SKILL_SHIELD, SkillLevel(1)),
        SkillTrait(SKILL_UNARMED, SkillLevel(1)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(2)),
    )
    .set_loadout(Loadout(
        # Shortbow, Arrows
        LoadoutChoice([
            (1, [WEAPON_BATTLEAXE, SkillTrait(SKILL_AXE, SkillLevel(1))]),
            (1, [WEAPON_FALCHION, SkillTrait(SKILL_BLADE, SkillLevel(1))]),
            (1, [WEAPON_MACE, SkillTrait(SKILL_MACE, SkillLevel(1))]),
        ]),
        LoadoutChoice([(1, SHIELD_SMALL), (1, SHIELD_BUCKLER)]),
        LoadoutChoice([
            (1, Armor(IRON_HELMET, SPECIES_ORC)),
            (2, Armor(LEATHER_HELMET, SPECIES_ORC)),
            (2, Armor(LEATHER_CAP, SPECIES_ORC)),
            (3, None),
        ]),
        LoadoutChoice([
            (1, Armor(HIDE_ARMOR, SPECIES_ORC)),
            (1, Armor(LEATHER_ARMOR, SPECIES_ORC)),
        ]),
        LoadoutChoice([
            (3, Armor(IRON_BRIGANDINE_CUIRASS, SPECIES_ORC)),
            (2, None),
        ])
    ))
)