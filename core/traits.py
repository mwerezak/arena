from typing import Any
from core.contest import Contest, SkillLevel

# traits are just simple data containers that can be attached to Creatures and queried
class CreatureTrait:
    name: str
    key: Any

    def __init__(self, **data):
        for name, value in data.items():
            super().__setattr__(name, value)

    def __setattr__(self, name, value):
        raise TypeError

    @property
    def key(self) -> Any:
        return type(self)

# supertype for traits that represent learned skills and abilities
class FeatTrait(CreatureTrait): pass

class SkillTrait(FeatTrait):
    skill: Contest
    level: SkillLevel

    def __init__(self, skill: Contest, level: SkillLevel):
        name = f'{skill.name} {level}'
        super().__init__(name = name, skill = skill, level = level)

    @property
    def key(self) -> Any:
        return super().key, self.skill