from __future__ import annotations
from typing import TYPE_CHECKING, Any

from core.traits import Trait
if TYPE_CHECKING:
    from core.contest import Contest, SkillLevel

# supertype for traits that apply to creatures
class CreatureTrait(Trait):
    pass

# supertype for traits that represent learned skills and abilities
class FeatTrait(CreatureTrait):
    pass

class SkillTrait(FeatTrait):
    skill: Contest
    level: SkillLevel

    def __init__(self, skill: Contest, level: SkillLevel):
        name = f'{skill.name} {level}'
        super().__init__(name = name, skill = skill, level = level)

    @property
    def key(self) -> Any:
        return SkillTrait, self.skill

# TODO implement
class EvadeTrait(FeatTrait):
    name = 'Improved Evade'
    desc = 'When this creature evades, it may make an Acrobatics check to avoid falling prone.'

class FinesseTrait(FeatTrait):
    name = 'Combat Finesse'
    desc = 'This creature may replace STR with DEX when making an attack or defence roll in melee combat.'

class MartialArtistTrait(FeatTrait):
    name = 'Martial Artist'
    desc = 'This creature can used unarmed attacks to parry even when outside of reach.'
