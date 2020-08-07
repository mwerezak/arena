from core.unarmed import NaturalWeaponTemplate, NaturalWeapon
from core.combat.damage import DamageType
from core.bodyplan import Morphology
from core.creature import CreatureTemplate
from core.constants import CreatureSize
from defines.bodyplan import HUMANOID, HUMANOID_NOTAIL

## Natural Weapon Templates

UNARMED_PUNCH = NaturalWeaponTemplate('Punch',  DamageType.Bludgeon)
UNARMED_CLAW  = NaturalWeaponTemplate('Claw',   DamageType.Slashing)
UNARMED_PAW   = NaturalWeaponTemplate('Strike', DamageType.Bludgeon)
UNARMED_WING  = NaturalWeaponTemplate('Strike', DamageType.Bludgeon, reach=+1)

UNARMED_KICK      = NaturalWeaponTemplate('Kick', DamageType.Bludgeon, reach=+1, force=-1)
UNARMED_KICK_QUAD = NaturalWeaponTemplate('Kick', DamageType.Bludgeon, reach=+1)  # quadripeds can kick out with more force

UNARMED_HOOF_BIPED = NaturalWeaponTemplate('Kick', DamageType.Bludgeon, armpen=+1, reach=+1, force=-1)
UNARMED_HOOF       = NaturalWeaponTemplate('Kick', DamageType.Bludgeon, armpen=+2, reach=+1)

UNARMED_BITE       = NaturalWeaponTemplate('Bite', DamageType.Puncture, reach=-1, damage=+1)
UNARMED_BITE_CRUSH = NaturalWeaponTemplate('Bite', DamageType.Bludgeon, reach=-1, damage=+1, armpen=-1)
UNARMED_BITE_WEAK  = NaturalWeaponTemplate('Bite', DamageType.Puncture, reach=-1, damage=+1, force=-1)

UNARMED_BEAK_PECK = NaturalWeaponTemplate('Peck', DamageType.Puncture, damage=+1)
UNARMED_BEAK_TEAR = NaturalWeaponTemplate('Bite', DamageType.Slashing, reach=-1, damage=+1)

UNARMED_HORN = NaturalWeaponTemplate('Gore', DamageType.Puncture, damage=+1)
UNARMED_TUSK = NaturalWeaponTemplate('Gore', DamageType.Puncture, force=-1, damage=+1)

UNARMED_TAIL = NaturalWeaponTemplate('Strike', DamageType.Bludgeon, reach=+2)

## Species

# the bodyplan for hominid humanoids... humans, dwarves, elves, orcs, goblins, etc...
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
    .attributes(DEX=+1, CON=+1, SIZ=-4, POW=-1, CHA=-2)
)

BODYPLAN_GNOLL = (
    Morphology(HUMANOID)
    .select('*')
        .set(armor = 1)
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
    .attributes(STR=+2, CON=+1, SIZ=+2, INT=-1, CHA=-1)
)

BODYPLAN_SATYR = (
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

SPECIES_SATYR = (
    CreatureTemplate('Satyr', BODYPLAN_SATYR)
    .attributes(DEX=+1, CON=+1, INT=+1, POW=+1, CHA=+1)
)

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
        .add_unarmed_attack(NaturalWeapon(UNARMED_BITE_CRUSH))
    .finalize()
)

SPECIES_MINOTAUR = (
    CreatureTemplate('Minotaur', BODYPLAN_MINOTAUR)
    .attributes(STR=+4, CON=+3, SIZ=+6)
)

if __name__ == '__main__':
    from core.combat.attack import MeleeAttack
    def print_attack(attack: MeleeAttack):
        print(f'*** {attack.name} ***')
        print(f'force: {attack.force}')
        print(f'reach: {attack.max_reach} - {attack.min_reach}')
        print(f'damage: {attack.damage}' + (f'/{attack.armor_pen}*' if attack.armor_pen is not None else ''))

    for id_tag, attack in SPECIES_MINOTAUR.get_unarmed_attacks():
        print_attack(attack)
        print(f'location: {id_tag}')
        print()