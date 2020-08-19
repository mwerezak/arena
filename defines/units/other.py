from __future__ import annotations
from typing import TYPE_CHECKING

from core.creature.template import CreatureTemplate
from core.creature.bodyplan import Morphology
from core.combat.unarmed import NaturalWeaponTemplate, NaturalWeapon
from core.combat.damage import DamageType
from core.combat.attacktraits import FormidableNatural
from defines.bodyplan import QUADRUPED_PACHYDERM, QUADRUPED_CANIFORME
from defines.species import UNARMED_KICK_QUAD, UNARMED_TUSK, UNARMED_BITE_WEAK, UNARMED_BITE, UNARMED_PAW, UNARMED_CLAW
from defines.traits import *

if TYPE_CHECKING:
    pass

# Elephant
UNARMED_TRUNK = NaturalWeaponTemplate('Strike', DamageType.Bludgeon, force=-1)

BODYPLAN_ELEPHANT = (
    Morphology(QUADRUPED_PACHYDERM)
    .select('*')
        .set(armor = 7) # thick hide
    .select('trunk')
        .add_unarmed_attack(NaturalWeapon(UNARMED_TRUNK))
    .select('head')
        .add_unarmed_attack(NaturalWeapon(UNARMED_TUSK, force=-1, reach=+1))
        .add_unarmed_attack(NaturalWeapon(UNARMED_BITE_WEAK))
    .select('l_leg', 'r_leg')
        .add_unarmed_attack(NaturalWeapon(UNARMED_KICK_QUAD))
    .select('l_arm', 'r_arm')
        .add_unarmed_attack(NaturalWeapon(UNARMED_KICK_QUAD, reach=-1, force=-1))
    .select('tail')
        .set(size = 0.1)
    .finalize()
)

SPECIES_ELEPHANT = (
    CreatureTemplate('Elephant', BODYPLAN_ELEPHANT)
    .set_attributes(STR=+8, CON=+5, SIZ=+30)
    .add_trait(
        SkillTrait(SKILL_UNARMED, SkillLevel(1)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(2)),
        SkillTrait(SKILL_WILLPOWER, SkillLevel(1)),
    )
)

# Bears
BODYPLAN_BEAR = (
    Morphology(QUADRUPED_CANIFORME)
    .select('*')
        .set(armor = 2) #thick pelt
    .select('head')
        .add_unarmed_attack(NaturalWeapon(UNARMED_BITE))
    .select('l_arm', 'r_arm')
        .add_unarmed_attack(NaturalWeapon(UNARMED_CLAW, force=+1, reach=+1, traits=[FormidableNatural()]))
        .add_unarmed_attack(NaturalWeapon(UNARMED_PAW, force=-1))
    .select('lbody')
        .set(size = 3.5)
    .select('l_leg', 'r_leg')
        .add_unarmed_attack(NaturalWeapon(UNARMED_KICK_QUAD, force=-1))
    .select('tail')
        .set(size = 0.5)
    .finalize()
)

SPECIES_BEAR = (
    CreatureTemplate('Black Bear', BODYPLAN_BEAR)
    .set_attributes(STR=+3, DEX=+2, CON=+2, SIZ=+3, CHA=-1)  #semi-solitary
    .add_trait(
        SkillTrait(SKILL_UNARMED, SkillLevel(2)),
        SkillTrait(SKILL_ENDURANCE, SkillLevel(2)),
        SkillTrait(SKILL_EVADE, SkillLevel(2)),
    )
)

SPECIES_BROWN_BEAR = (
    CreatureTemplate('Brown Bear', template=SPECIES_BEAR)
    .set_attributes(STR=+5, SIZ=+7)
)

BODYPLAN_GRIZZLY = (
    Morphology(BODYPLAN_BEAR)
    .select('*')
    .set(armor = 3) #thicker pelt
    .finalize()
)

SPECIES_GRIZZY = (
    CreatureTemplate('Grizzly Bear', BODYPLAN_GRIZZLY, template=SPECIES_BEAR)
    .set_attributes(STR=+7, SIZ=+10)
)