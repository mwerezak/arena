from core.creature.template import CreatureTemplate
from defines.species import SPECIES_HORSE
from defines.traits import *

CREATURE_RIDING_HORSE = (
    CreatureTemplate('Horse', template=SPECIES_HORSE)
    .modify_attributes(POW=-2)  # domestication
)

CREATURE_WAR_HORSE = (
    CreatureTemplate('War Horse', template=SPECIES_HORSE)
    .modify_attributes(STR=+2, SIZ=+3, POW=-1)
    .add_trait(
        SkillTrait(SKILL_ENDURANCE, SkillLevel(2)),
        SkillTrait(SKILL_UNARMED, SkillLevel(1)),
    )
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