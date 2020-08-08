from core.creature import CreatureTemplate
from core.loadout import Loadout, LoadoutGroup, LoadoutChoice
from core.equipment.armor import Armor
from defines.species import SPECIES_SATYR, SPECIES_MINOTAUR, SPECIES_GNOLL
from defines.traits import *
from defines.weapons import (
    WEAPON_SPEAR, WEAPON_HALFSPEAR,
)
from defines.shields import (
    SHIELD_SMALL, SHIELD_MEDIUM
)
from defines.armor import (
    LINEN_CUIRASS,
)

UNIT_SATYR_BRAVE = (
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
        LoadoutChoice([(1, Armor(LINEN_CUIRASS, SPECIES_SATYR)), (1, [])])
    ))
)

if __name__ == '__main__':
    from core.creature import Creature
    c = Creature(UNIT_SATYR_BRAVE)