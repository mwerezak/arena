from core.creature.template import CreatureTemplate

class FormationTemplate:
    def __init__(self, name: str, creature: CreatureTemplate, mount: CreatureTemplate = None):
        self.name = name
        self.creature = creature
        self.mount = mount  # mounted formations
