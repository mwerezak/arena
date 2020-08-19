from core.creature.template import CreatureTemplate
from core.creature.loadout import Loadout, LoadoutChoice
from core.equipment.armor import ArmorTemplate, Armor
from defines.species import SPECIES_HUMAN
from defines.units.horses import CREATURE_RIDING_HORSE, CREATURE_WAR_HORSE
from defines.armor import (
    ARMORTYPE_PADDED, ARMORTYPE_LAMINATED, ARMORTYPE_SCALED, ARMORTYPE_MAIL,
    MATERIAL_LINEN, MATERIAL_LEATHER, MATERIAL_STEEL,
    PATTERN_ARMOR, PATTERN_HAUBERK, PATTERN_SUIT, PATTERN_HELMET,
)
from defines.weapons import (
    WEAPON_BROADSWORD, WEAPON_SHORTSWORD, WEAPON_DAGGER, WEAPON_LONGSPEAR, WEAPON_MACE,
)
from defines.shields import SHIELD_SMALL, SHIELD_MEDIUM, SHIELD_LARGE
from defines.traits import *


PADDED_DOUBLET  = ArmorTemplate('Doublet', ARMORTYPE_PADDED, MATERIAL_LINEN, PATTERN_ARMOR)
PADDED_GAMBESON = ArmorTemplate('Gambeson', ARMORTYPE_PADDED, MATERIAL_LINEN, PATTERN_SUIT)
PADDED_CAP      = ArmorTemplate('Cap', ARMORTYPE_PADDED, MATERIAL_LINEN, PATTERN_HELMET)

# LEATHER_CUIRASS    = ArmorTemplate('Cuirass', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_CUIRASS)
# LEATHER_ARMOR      = ArmorTemplate('Armor', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_ARMOR)
# LEATHER_ARMOR_SUIT = ArmorTemplate('Armor Suit', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_SUIT)
#
# STEEL_BRIGANDINE_CUIRASS = ArmorTemplate('Brigandine Cuirass', ARMORTYPE_SCALED, MATERIAL_STEEL, PATTERN_CUIRASS)
STEEL_BRIGANDINE_HAUBERK = ArmorTemplate('Brigandine Hauberk', ARMORTYPE_SCALED, MATERIAL_STEEL, PATTERN_HAUBERK)
#
# STEEL_MAIL_SHIRT   = ArmorTemplate('Mail Shirt', ARMORTYPE_MAIL, MATERIAL_STEEL, PATTERN_CUIRASS)
STEEL_MAIL_HAUBERK = ArmorTemplate('Mail Hauberk', ARMORTYPE_MAIL, MATERIAL_STEEL, PATTERN_HAUBERK)
# STEEL_MAIL_SUIT    = ArmorTemplate('Mail Suit', ARMORTYPE_MAIL, MATERIAL_STEEL, PATTERN_SUIT)
#
# STEEL_BANDED_MAIL_CUIRASS = ArmorTemplate('Banded Plate Cuirass', ARMORTYPE_BANDED, MATERIAL_STEEL, PATTERN_CUIRASS)
# STEEL_BANDED_MAIL_ARMOR   = ArmorTemplate('Banded Plate Armor (Half-Suit)', ARMORTYPE_BANDED, MATERIAL_STEEL, PATTERN_ARMOR)
#
# STEEL_HALF_PLATE_CUIRASS = ArmorTemplate('Half-Plate Cuirass', ARMORTYPE_HALF_PLATE, MATERIAL_STEEL, PATTERN_CUIRASS)
# STEEL_HALF_PLATE_ARMOR   = ArmorTemplate('Half-Plate Armor (Half-Suit)', ARMORTYPE_HALF_PLATE, MATERIAL_STEEL, PATTERN_ARMOR)
#
# STEEL_PLATE_MAIL_CUIRASS = ArmorTemplate('Splinted Plate Cuirass', ARMORTYPE_SPLINTED, MATERIAL_STEEL, PATTERN_CUIRASS)
# STEEL_PLATE_MAIL_ARMOR   = ArmorTemplate('Splinted Plate Armor (Half-Suit)', ARMORTYPE_SPLINTED, MATERIAL_STEEL, PATTERN_ARMOR)
# STEEL_PLATE_MAIL_SUIT    = ArmorTemplate('Splinted Plate Armor', ARMORTYPE_SPLINTED, MATERIAL_STEEL, PATTERN_SUIT)
#
# STEEL_FULL_PLATE_CUIRASS = ArmorTemplate('Full-Plate Cuirass', ARMORTYPE_FULL_PLATE, MATERIAL_STEEL, PATTERN_CUIRASS)
# STEEL_FULL_PLATE_ARMOR   = ArmorTemplate('Full-Plate Armor (Half-Suit)', ARMORTYPE_FULL_PLATE, MATERIAL_STEEL, PATTERN_ARMOR)
# STEEL_FULL_PLATE_SUIT    = ArmorTemplate('Full-Plate Armor', ARMORTYPE_FULL_PLATE, MATERIAL_STEEL, PATTERN_SUIT)

LEATHER_CAP    = ArmorTemplate('Cap', ARMORTYPE_PADDED, MATERIAL_LEATHER, PATTERN_HELMET)
LEATHER_HELMET = ArmorTemplate('Helmet', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_HELMET)

STEEL_HELMET    = ArmorTemplate('Kettle Helmet', ARMORTYPE_SCALED, MATERIAL_STEEL, PATTERN_HELMET)
# STEEL_GREATHELM = ArmorTemplate('Great Helmet', ARMORTYPE_MAIL, MATERIAL_STEEL, PATTERN_HELMET)
#
# STEEL_MORION    = ArmorTemplate('Morion Helmet', ARMORTYPE_SCALED, MATERIAL_STEEL, PATTERN_HELMET)
# STEEL_CLOSEHELM = ArmorTemplate('Close Helmet', ARMORTYPE_SPLINTED, MATERIAL_STEEL, PATTERN_HELMET)
# STEEL_ARMET     = ArmorTemplate('Armet', ARMORTYPE_FULL_PLATE, MATERIAL_STEEL, PATTERN_HELMET)


CREATURE_LEVY_SPEARMAN = (
    CreatureTemplate('Levy Spearman', template=SPECIES_HUMAN)
    .add_trait(SkillTrait(SKILL_SHIELD, SkillLevel(1)))
    .set_loadout(Loadout(
        [WEAPON_LONGSPEAR, SHIELD_MEDIUM],
        LoadoutChoice([(3, WEAPON_DAGGER), (2, WEAPON_SHORTSWORD), (5, None)]),
        LoadoutChoice([(1, Armor(PADDED_GAMBESON, SPECIES_HUMAN)), (4, Armor(PADDED_DOUBLET, SPECIES_HUMAN)), (5, None)]),
        LoadoutChoice([(2, Armor(LEATHER_HELMET, SPECIES_HUMAN)), (2, Armor(LEATHER_CAP, SPECIES_HUMAN)), (1, None)]),
    ))
)

CREATURE_LEVY_ARCHER = (
    CreatureTemplate('Levy Archer', template=SPECIES_HUMAN)
    .add_trait(SkillTrait(SKILL_BOW, SkillLevel(1)))
    .set_loadout(Loadout(
        # Longbow, Arrows
        LoadoutChoice([(1, WEAPON_SHORTSWORD), (3, WEAPON_DAGGER), (2, None)]),
        LoadoutChoice([(1, Armor(PADDED_DOUBLET, SPECIES_HUMAN)), (3, None)]),
        LoadoutChoice([(3, Armor(LEATHER_CAP, SPECIES_HUMAN)), (3, Armor(PADDED_CAP, SPECIES_HUMAN)), (5, None)]),
    ))
)

CREATURE_SERGEANT_SPEARMAN = (
    CreatureTemplate('Sergeant Spearman', template=SPECIES_HUMAN)
    .add_trait(
        SkillTrait(SKILL_POLEARM, SkillLevel(2)),
        SkillTrait(SKILL_SHIELD, SkillLevel(2)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(1)),
    )
    .set_loadout(Loadout(
        [WEAPON_LONGSPEAR],
        LoadoutChoice([(3, SHIELD_LARGE), (1, SHIELD_MEDIUM)]),
        LoadoutChoice([
            (1, [WEAPON_BROADSWORD, SkillTrait(SKILL_BLADE, SkillLevel(2))]),
            (2, [WEAPON_SHORTSWORD, SkillTrait(SKILL_BLADE, SkillLevel(1))]),
            (3, [WEAPON_MACE, SkillTrait(SKILL_MACE, SkillLevel(1))]),
        ]),
        LoadoutChoice([(3, Armor(STEEL_HELMET, SPECIES_HUMAN)), (1, Armor(LEATHER_HELMET, SPECIES_HUMAN))]),
        [Armor(PADDED_DOUBLET, SPECIES_HUMAN)],
        LoadoutChoice([(1, Armor(STEEL_MAIL_HAUBERK, SPECIES_HUMAN)), (3, Armor(STEEL_BRIGANDINE_HAUBERK, SPECIES_HUMAN))]),
    ))
)

