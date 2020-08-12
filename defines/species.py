from core.combat.unarmed import NaturalWeaponTemplate, NaturalWeapon
from core.combat.damage import DamageType
from core.creature.bodyplan import Morphology
from core.creature.template import CreatureTemplate
from defines.bodyplan import HUMANOID, HUMANOID_NOTAIL, QUADRUPED_UNGULATE
from defines.traits import *

## Natural Weapon Templates

UNARMED_PUNCH = NaturalWeaponTemplate('Punch',  DamageType.Bludgeon)
UNARMED_CLAW  = NaturalWeaponTemplate('Claw',   DamageType.Slashing)
UNARMED_PAW   = NaturalWeaponTemplate('Strike', DamageType.Bludgeon)
UNARMED_WING  = NaturalWeaponTemplate('Strike', DamageType.Bludgeon, reach=+1)

UNARMED_KICK      = NaturalWeaponTemplate('Kick', DamageType.Bludgeon, reach=+1, force=-1)
UNARMED_KICK_QUAD = NaturalWeaponTemplate('Kick', DamageType.Bludgeon, reach=+1)  # quadripeds can kick out with more force

UNARMED_HOOF_BIPED = NaturalWeaponTemplate('Kick', DamageType.Bludgeon, armpen=+1, reach=+1, force=-1)
UNARMED_HOOF       = NaturalWeaponTemplate('Kick', DamageType.Bludgeon, armpen=+1, reach=+1)

UNARMED_BITE       = NaturalWeaponTemplate('Bite', DamageType.Puncture, reach=-1, damage=+1)
UNARMED_BITE_CRUSH = NaturalWeaponTemplate('Bite', DamageType.Bludgeon, reach=-1, damage=+1, armpen=-1)
UNARMED_BITE_WEAK  = NaturalWeaponTemplate('Bite', DamageType.Puncture, reach=-1, damage=+1, force=-1)

UNARMED_BEAK_PECK = NaturalWeaponTemplate('Peck', DamageType.Puncture, damage=+1)
UNARMED_BEAK_TEAR = NaturalWeaponTemplate('Bite', DamageType.Slashing, reach=-1, damage=+1)

UNARMED_HORN = NaturalWeaponTemplate('Gore', DamageType.Puncture, damage=+1)
UNARMED_TUSK = NaturalWeaponTemplate('Gore', DamageType.Puncture, force=-1, damage=+1)

UNARMED_TAIL = NaturalWeaponTemplate('Strike', DamageType.Bludgeon, reach=+2)

## Species

# Humanlike humanoids... humans, dwarves, elves, orcs, goblins, etc...
BODYPLAN_HUMANLIKE = (
    Morphology(HUMANOID_NOTAIL)
    .select('l_arm', 'r_arm')
        .add_unarmed_attack(NaturalWeapon(UNARMED_PUNCH, force=-1))
    .select('l_leg', 'r_leg')
        .add_unarmed_attack(NaturalWeapon(UNARMED_KICK))
    .select('head')
        .add_unarmed_attack(NaturalWeapon(UNARMED_BITE_WEAK, force=-1))
    .finalize()
)

SPECIES_HUMAN = (
    CreatureTemplate('Human', BODYPLAN_HUMANLIKE)
)

SPECIES_GOBLIN = (
    CreatureTemplate('Goblin', BODYPLAN_HUMANLIKE)
    .set_attributes(DEX=+1, CON=+1, SIZ=-4, POW=-1, CHA=-2)
)

SPECIES_ORC = (
    CreatureTemplate('Orc', BODYPLAN_HUMANLIKE)
    .set_attributes(STR=+3, CON=+1, SIZ=+1, INT=-1, POW=-2, CHA=-2)
)

SPECIES_OGRE = (
    CreatureTemplate('Ogre', BODYPLAN_HUMANLIKE)
    .set_attributes(STR=+4, DEX=-1, CON=+3, SIZ=+10, INT=-2, CHA=-2)
)

# Horses
BODYPLAN_HORSE = (
    Morphology(QUADRUPED_UNGULATE)
    .select('*')
        .set(armor = 1)  # thick hide
    .select('l_leg', 'r_leg')
        .add_unarmed_attack(NaturalWeapon(UNARMED_HOOF))
    .select('l_arm', 'r_arm')
        .add_unarmed_attack(NaturalWeapon(UNARMED_HOOF, reach=-1, force=-1))  # can't kick out as far with front legs
    .select('head')
        .add_unarmed_attack(NaturalWeapon(UNARMED_BITE_WEAK))
    .finalize()
)

SPECIES_HORSE = (
    CreatureTemplate('Horse', BODYPLAN_HORSE)
    .set_attributes(STR=+6, CON=+2, SIZ=+12, INT=-2)
    .add_trait(SkillTrait(SKILL_ENDURANCE, SkillLevel(1)))
)

# Gnolls
BODYPLAN_GNOLL = (
    Morphology(HUMANOID)
    .select('*')
        .set(armor = 1)  # thick fur
    .select('tail')
        .set(size = 1.5)
    .select('l_arm', 'r_arm')
        .add_unarmed_attack(NaturalWeapon(UNARMED_PUNCH, force=-1))
        .add_unarmed_attack(NaturalWeapon(UNARMED_CLAW, force=-1))
    .select('l_leg', 'r_leg')
        .add_unarmed_attack(NaturalWeapon(UNARMED_KICK))
    .select('head')
        .add_unarmed_attack(NaturalWeapon(UNARMED_BITE))
    .finalize()
)

SPECIES_GNOLL = (
    CreatureTemplate('Gnoll', BODYPLAN_GNOLL)
    .set_attributes(STR=+2, CON=+1, SIZ=+2, INT=-1, POW=+1, CHA=-1)
    .add_trait(
        SkillTrait(SKILL_UNARMED, SkillLevel(1))
    )
)

# Satyrs

# goatlike lower body, humanlike upper body
BODYPLAN_SATYR_HALF = (
    Morphology(HUMANOID)
    .select('lbody', 'l_leg', 'r_leg', 'tail')
        .set(armor = 1) #thick fur on the lower body, thin at the top
    .select('tail')
        .set(size = 0.5) # goat tail is fairly small
    .select('l_arm', 'r_arm')
        .add_unarmed_attack(NaturalWeapon(UNARMED_PUNCH, force=-1))
    .select('l_leg', 'r_leg')
        .add_unarmed_attack(NaturalWeapon(UNARMED_HOOF_BIPED))
    .select('head')
        .add_unarmed_attack(NaturalWeapon(UNARMED_HORN, force=-1, reach=-1)) #small horns
        .add_unarmed_attack(NaturalWeapon(UNARMED_BITE_WEAK, force=-1))
    .finalize()
)

SPECIES_SATYR_HALF = (
    CreatureTemplate('Satyr', BODYPLAN_SATYR_HALF)
    .set_attributes(DEX=+1, CON=+1, INT=+1, POW=+2, CHA=+1)
    .add_trait(EvadeTrait, FinesseTrait)
)


# goat from head to toe
BODYPLAN_SATYR_FULL = (
    Morphology(HUMANOID)
    .select('*')
        .set(armor = 1) #thick fur on the lower body, thin at the top
    .select('tail')
        .set(size = 0.5) # goat tail is fairly small
    .select('l_arm', 'r_arm')
        .add_unarmed_attack(NaturalWeapon(UNARMED_PUNCH, force=-1))
    .select('l_leg', 'r_leg')
        .add_unarmed_attack(NaturalWeapon(UNARMED_HOOF_BIPED))
    .select('head')
        .add_unarmed_attack(NaturalWeapon(UNARMED_HORN)) #full size goat horns
        .add_unarmed_attack(NaturalWeapon(UNARMED_BITE_WEAK))
    .finalize()
)

SPECIES_SATYR = (
    CreatureTemplate('Satyr', BODYPLAN_SATYR_FULL)
    .set_attributes(DEX=+1, CON=+1, SIZ=+1, INT=+1, POW=+2)
    .add_trait(EvadeTrait, FinesseTrait)
)


# Minotaur
BODYPLAN_MINOTAUR = (
    Morphology(HUMANOID)
    .select('*')
        .set(armor = 1) #thick hide
    .select('tail')
        .set(size = 2)
    .select('l_arm', 'r_arm')
        .add_unarmed_attack(NaturalWeapon(UNARMED_PUNCH, force=-1))
    .select('l_leg', 'r_leg')
        .add_unarmed_attack(NaturalWeapon(UNARMED_HOOF_BIPED))
    .select('head')
        .add_unarmed_attack(NaturalWeapon(UNARMED_HORN))
        .add_unarmed_attack(NaturalWeapon(UNARMED_BITE_WEAK))
    .finalize()
)

SPECIES_MINOTAUR = (
    CreatureTemplate('Minotaur', BODYPLAN_MINOTAUR)
    .set_attributes(STR=+4, CON=+3, SIZ=+6)
    .add_trait(SkillTrait(SKILL_ENDURANCE, SkillLevel(1)))
)
