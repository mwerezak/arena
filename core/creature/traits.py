from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
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

    def __repr__(self) -> str:
        ignore = ['name', 'key']
        data = ', '.join(
            f'{k}={v!r}' for k,v in self.__dict__.items() if k not in ignore
        )
        return f'{self.__class__.__name__}({data})'

# supertype for traits that represent learned skills and abilities
class FeatTrait(CreatureTrait):
    pass

class SkillTrait(FeatTrait):
    skill: 'Contest'
    level: 'SkillLevel'

    def __init__(self, skill: 'Contest', level: 'SkillLevel'):
        name = f'{skill.name} {level}'
        super().__init__(name = name, skill = skill, level = level)

    @property
    def key(self) -> Any:
        return SkillTrait, self.skill

class EvadeTrait(FeatTrait):
    name = 'Improved Evade'
EvadeTrait = EvadeTrait()  # no args, so just lock it down

class FinesseTrait(FeatTrait):
    name = 'Combat Finesse'
FinesseTrait = FinesseTrait()