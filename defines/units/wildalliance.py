from core.creature import CreatureTemplate
from core.loadout import Loadout, LoadoutGroup, LoadoutChoice
from core.equipment.armor import Armor, ArmorTemplate
from defines.species import SPECIES_SATYR, SPECIES_MINOTAUR, SPECIES_GNOLL, SPECIES_HORSE
from defines.traits import *
from defines.weapons import (
    WEAPON_SPEAR, WEAPON_HALFSPEAR, WEAPON_LONGSPEAR, WEAPON_SHORTSWORD, WEAPON_SCIMITAR, WEAPON_DAGGER,
    WEAPON_BATTLEAXE, WEAPON_MINOTAUR_AXE, WEAPON_MACE, WEAPON_GREATAXE,
)
from defines.shields import (
    SHIELD_SMALL, SHIELD_MEDIUM
)
from defines.armor import (
    PATTERN_HELMET, PATTERN_CUIRASS, PATTERN_ARMOR, PATTERN_HAUBERK, PATTERN_CHESTPIECE, PATTERN_TAILGUARD,
    ARMORTYPE_LAMINATED, ARMORTYPE_SCALED, ARMORTYPE_HALF_PLATE, ARMORTYPE_PLATE_MAIL,
    MATERIAL_LINEN, MATERIAL_BRONZE, MATERIAL_LEATHER,
)

## Armor Templates

LINEN_CUIRASS = ArmorTemplate('Cuirass', ARMORTYPE_LAMINATED, MATERIAL_LINEN, PATTERN_CUIRASS)
LINEN_ARMOR = ArmorTemplate('Armor', ARMORTYPE_LAMINATED, MATERIAL_LINEN, PATTERN_ARMOR)

BRONZE_HELMET = ArmorTemplate('Helmet', ARMORTYPE_SCALED, MATERIAL_BRONZE, PATTERN_HELMET)
BRONZE_BARBUTE = ArmorTemplate('Barbute Helmet', ARMORTYPE_HALF_PLATE, MATERIAL_BRONZE, PATTERN_HELMET)
BRONZE_SCALE_CUIRASS = ArmorTemplate('Scale Cuirass', ARMORTYPE_SCALED, MATERIAL_BRONZE, PATTERN_CUIRASS)
BRONZE_SCALE_HAUBERK = ArmorTemplate('Scale Hauberk', ARMORTYPE_SCALED, MATERIAL_BRONZE, PATTERN_HAUBERK)
BRONZE_HALF_PLATE_CUIRASS = ArmorTemplate('Half-Plate Cuirass', ARMORTYPE_HALF_PLATE, MATERIAL_BRONZE, PATTERN_CUIRASS)
BRONZE_PLATE_MAIL_CUIRASS = ArmorTemplate('Splinted Plate Cuirass', ARMORTYPE_PLATE_MAIL, MATERIAL_BRONZE, PATTERN_CUIRASS)
BRONZE_PLATE_MAIL_ARMOR = ArmorTemplate('Splinted Plate Armor (Half-Suit)', ARMORTYPE_PLATE_MAIL, MATERIAL_BRONZE, PATTERN_ARMOR)

LINEN_HAUBERK = ArmorTemplate('Apron', ARMORTYPE_LAMINATED, MATERIAL_LINEN, PATTERN_HAUBERK)
LINEN_TAILGUARD = ArmorTemplate('Tailguard', ARMORTYPE_LAMINATED, MATERIAL_LINEN, PATTERN_TAILGUARD)

LEATHER_CUIRASS    = ArmorTemplate('Cuirass', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_CUIRASS)
LEATHER_ARMOR      = ArmorTemplate('Armor', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_ARMOR)
BRONZE_PLATE_CHESTPIECE = ArmorTemplate('Plate Chestpiece', ARMORTYPE_HALF_PLATE, MATERIAL_BRONZE, PATTERN_CHESTPIECE)

## Unit Templates

CREATURE_SATYR_BRAVE = (
    CreatureTemplate('Satyr Brave', template = SPECIES_SATYR)
    .add_trait(
        SkillTrait(SKILL_POLEARM, SkillLevel(1)),
        SkillTrait(SKILL_SHIELD, SkillLevel(1)),
        SkillTrait(SKILL_STEALTH, SkillLevel(1)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(1)),
    )
    .set_loadout(Loadout(
        LoadoutChoice([(1, WEAPON_SPEAR), (1, WEAPON_HALFSPEAR)]),
        LoadoutChoice([(1, SHIELD_MEDIUM), (1, SHIELD_SMALL)]),
        LoadoutChoice([(1, Armor(LINEN_CUIRASS, SPECIES_SATYR)), (1, None)])
    ))
)

CREATURE_SATYR_ARCHER = (
    CreatureTemplate('Satyr Skirmisher', template = SPECIES_SATYR)
    .add_trait(
        SkillTrait(SKILL_BOW, SkillLevel(2)),
        SkillTrait(SKILL_BLADE, SkillLevel(1)),
        SkillTrait(SKILL_STEALTH, SkillLevel(1)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(1)),
    )
    .set_loadout(Loadout(
        [], # Bow, Arrows
        LoadoutChoice([(1, WEAPON_SHORTSWORD), (1, WEAPON_DAGGER)]),
    ))
)

CREATURE_SATYR_WARRIOR = (
    CreatureTemplate('Satyr Warrior', template = SPECIES_SATYR)
    .add_trait(
        SkillTrait(SKILL_SHIELD, SkillLevel(1)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(2)),
    )
    .set_loadout(Loadout(
        LoadoutChoice([
            (4, [WEAPON_SPEAR, SHIELD_MEDIUM, SkillTrait(SKILL_POLEARM, SkillLevel(2))]),
            (3, [WEAPON_SHORTSWORD, SHIELD_SMALL, SkillTrait(SKILL_BLADE, SkillLevel(2))]),
            (3, [WEAPON_SCIMITAR, SHIELD_MEDIUM, SkillTrait(SKILL_BLADE, SkillLevel(2))]),
        ]),
        [ Armor(LINEN_ARMOR, SPECIES_SATYR) ],
        LoadoutChoice([(1, Armor(BRONZE_HELMET, SPECIES_SATYR)), (1, None)]),
        LoadoutChoice([(3, Armor(BRONZE_SCALE_CUIRASS, SPECIES_SATYR)), (1, None)]),
    ))
)

CREATURE_SATYR_WARDEN = (
    CreatureTemplate('Satyr Warden', template = SPECIES_SATYR)
    .modify_attributes(DEX=+1)
    .add_trait(
        SkillTrait(SKILL_BLADE, SkillLevel(3)),
        SkillTrait(SKILL_SHIELD, SkillLevel(3)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(3)),
    )
    .set_loadout(Loadout(
        [ WEAPON_SCIMITAR, SHIELD_MEDIUM, Armor(LINEN_ARMOR, SPECIES_SATYR) ],
        LoadoutChoice([(3, Armor(BRONZE_HELMET, SPECIES_SATYR)), (1, None)]),
        LoadoutChoice([(3, Armor(BRONZE_SCALE_HAUBERK, SPECIES_SATYR)), (1, Armor(BRONZE_HALF_PLATE_CUIRASS, SPECIES_SATYR))]),
    ))
)

CREATURE_SATYR_OUTRIDER = (
    CreatureTemplate('Satyr Outrider', template = SPECIES_SATYR)
    .add_trait(
        SkillTrait(SKILL_POLEARM, SkillLevel(2)),
        SkillTrait(SKILL_SHIELD, SkillLevel(2)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(3)),
        SkillTrait(SKILL_RIDING, SkillLevel(2)),
    )
    .set_loadout(Loadout(
        [WEAPON_LONGSPEAR],
        LoadoutChoice([(3, SHIELD_MEDIUM), (1, SHIELD_SMALL)]),
        LoadoutChoice([(1, Armor(LINEN_CUIRASS, SPECIES_SATYR)), (1, None)])
    ))
)

# companions of the satyr outriders
CREATURE_WILD_HORSE = (
    CreatureTemplate('Wild Horse', template = SPECIES_HORSE)
    .modify_attributes(SIZ=-4, POW=+1) # smaller but more personality
    .add_trait(
        SkillTrait(SKILL_ENDURANCE, SkillLevel(2)),
        SkillTrait(SKILL_UNARMED, SkillLevel(2)),
    )
)

CREATURE_MINOTAUR_MILITIA = (
    CreatureTemplate('Minotaur Militia', template=SPECIES_MINOTAUR)
    .add_trait(
        SkillTrait(SKILL_AXE, SkillLevel(1)),
        SkillTrait(SKILL_SHIELD, SkillLevel(1)),
    )
    .set_loadout(Loadout([
        WEAPON_BATTLEAXE,  # basically a hatchet for a minotaur
        SHIELD_SMALL,
        Armor(LINEN_HAUBERK, SPECIES_MINOTAUR),
    ]))
)

CREATURE_MINOTAUR_WARRIOR = (
    CreatureTemplate('Minotaur Protector', template=SPECIES_MINOTAUR)
    .modify_attributes(STR=+1)
    .add_trait(
        SkillTrait(SKILL_AXE, SkillLevel(3)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(3)),
        SkillTrait(SKILL_UNARMED, SkillLevel(2)),
    )
    .set_loadout(Loadout(
        [ WEAPON_MINOTAUR_AXE ],
        LoadoutChoice([(1, Armor(BRONZE_HELMET, SPECIES_MINOTAUR)), (1, None)]),
        [ Armor(LINEN_HAUBERK, SPECIES_MINOTAUR), Armor(BRONZE_HALF_PLATE_CUIRASS, SPECIES_MINOTAUR) ],
        LoadoutChoice([(3, Armor(LINEN_TAILGUARD, SPECIES_MINOTAUR)), (1, None)]),
    ))
)

CREATURE_MINOTAUR_CHAMPION = (
    CreatureTemplate('Minotaur Champion', template=SPECIES_MINOTAUR)
    .modify_attributes(STR=+1,CON=+1)
    .add_trait(
        SkillTrait(SKILL_AXE, SkillLevel(5)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(4)),
        SkillTrait(SKILL_UNARMED, SkillLevel(3)),
    )
    .set_loadout(Loadout(
        [ WEAPON_MINOTAUR_AXE ],
        LoadoutChoice([(1, Armor(BRONZE_BARBUTE, SPECIES_MINOTAUR)), (3, Armor(BRONZE_HELMET, SPECIES_MINOTAUR))]),
        [ Armor(LINEN_HAUBERK, SPECIES_MINOTAUR), Armor(LINEN_TAILGUARD, SPECIES_MINOTAUR) ],
        LoadoutChoice([(1, Armor(BRONZE_PLATE_MAIL_ARMOR, SPECIES_MINOTAUR)), (1, Armor(BRONZE_PLATE_MAIL_CUIRASS, SPECIES_MINOTAUR))]),
    ))
)

CREATURE_GNOLL_WARRIOR = (
    CreatureTemplate('Gnoll Warrior', template=SPECIES_GNOLL)
    .add_trait(
        SkillTrait(SKILL_SHIELD, SkillLevel(1)),
        SkillTrait(SKILL_UNARMED, SkillLevel(2)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(2)),
        EvadeTrait,
    )
    .set_loadout(Loadout(
        LoadoutChoice([
            (2, [WEAPON_BATTLEAXE, SkillTrait(SKILL_AXE, SkillLevel(2))]),
            (1, [WEAPON_MACE, SkillTrait(SKILL_MACE, SkillLevel(2))]),
        ]),
        LoadoutChoice([(2, SHIELD_MEDIUM), (1, SHIELD_SMALL)]),
        LoadoutChoice([(5, Armor(LEATHER_CUIRASS, SPECIES_GNOLL)), (3, Armor(BRONZE_SCALE_CUIRASS, SPECIES_GNOLL)), (1, None)])
    ))
)

CREATURE_GNOLL_CHIEFTAINS_SON = (
    CreatureTemplate('Gnoll Chieftain\'s Son', template=SPECIES_GNOLL)
    .modify_attributes(STR=+1)
    .add_trait(
        SkillTrait(SKILL_UNARMED, SkillLevel(3)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(3)),
        EvadeTrait,
    )
    .set_loadout(Loadout(
        LoadoutChoice([
            (1, [WEAPON_BATTLEAXE, SHIELD_MEDIUM, SkillTrait(SKILL_AXE, SkillLevel(3)), SkillTrait(SKILL_SHIELD, SkillLevel(1))]),
            (1, [WEAPON_GREATAXE, SkillTrait(SKILL_AXE, SkillLevel(4))]),
        ]),
        LoadoutChoice([(3, Armor(LEATHER_ARMOR, SPECIES_GNOLL)), (1, None)]),
        LoadoutChoice([(3, Armor(BRONZE_SCALE_HAUBERK, SPECIES_GNOLL)), (1, Armor(BRONZE_SCALE_CUIRASS, SPECIES_GNOLL))]),
        LoadoutChoice([(1, Armor(BRONZE_PLATE_CHESTPIECE, SPECIES_GNOLL)), (1, None)]),
    ))
)

if __name__ == '__main__':
    from core.combat.attack import MeleeAttack
    def print_attack(attack: MeleeAttack):
        print(f'*** {attack.name} ***')
        print(f'force: {attack.force}')
        print(f'reach: {attack.max_reach} - {attack.min_reach}')
        print(f'damage: {attack.damage}' + (f'/{attack.armor_pen}*' if attack.armor_pen is not None else ''))

    def print_creature_attacks(creature: CreatureTemplate):
        for bp_tag, weapon in creature.get_natural_weapons():
            print_attack(weapon.create_attack(creature))
            print(f'location: {bp_tag}')

    from defines.species import *
    from core.creature import Creature
