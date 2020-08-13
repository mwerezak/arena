from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.creature.template import CreatureTemplate

class FormationTemplate:
    def __init__(self, name: str, creature: CreatureTemplate, mount: CreatureTemplate = None):
        self.name = name
        self.creature = creature
        self.mount = mount  # mounted formations
