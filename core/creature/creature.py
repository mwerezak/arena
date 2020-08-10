from typing import MutableMapping, Optional, Iterable

from core.constants import MeleeRange
from core.combat.attack import MeleeAttack
from core.creature.combat import MeleeCombat
from core.creature.template import CreatureTemplate
from core.equipment import Equipment
from core.creature.traits import CreatureTrait
from core.action import Entity

class Creature(Entity):
    mount: Optional['Creature']  # if this creature is riding on another creature
    melee_combat: MutableMapping['Creature', MeleeCombat]

    def __init__(self, template: CreatureTemplate):
        self.template = template
        self.name = template.name
        self.health = template.max_health
        self.traits = { trait.key : trait for trait in template.get_traits() }

        self.mount = None
        self.melee_combat = {}

        self.unarmed_attacks = {
            (bp_tag, natural_weapon.create_attack(template))
            for bp_tag, natural_weapon in template.get_natural_weapons()
        }

        self.equipment = []
        template.loadout.apply_loadout(self)

    def add_trait(self, trait: CreatureTrait) -> None:
        self.traits[trait.key] = trait

    def add_equipment(self, equipment: Equipment) -> None:
        self.equipment.append(equipment)

    # health: float
    # template: CreatureTemplate
    # melee_combat: MutableMapping['Creature', 'MeleeCombat']
    # get_engage_range() -> MeleeRange
    # equipment

    ## Melee Combat

    def can_use_bodypart(self, bp_tag: str) -> bool:
        return True

    def get_melee_attacks(self) -> Iterable[MeleeAttack]:
        for bp_tag, attack in self.unarmed_attacks:
            if self.can_use_bodypart(bp_tag):
                yield attack
        for item in self.equipment:
            if hasattr(item, 'get_melee_attacks'):
                yield from item.get_melee_attacks()

    def get_melee_engage_distance(self) -> MeleeRange:
        attack_reach = (attack.max_reach for attack in self.get_melee_attacks())
        return max(attack_reach, default=MeleeRange(0))

    def get_melee_combat(self, other: 'Creature') -> Optional[MeleeCombat]:
        return self.melee_combat.get(other, None)

    def add_melee_combat(self, other: 'Creature', melee: MeleeCombat) -> None:
        self.melee_combat[other] = melee

    def remove_melee_combat(self, other: 'Creature') -> None:
        if other in self.melee_combat:
            del self.melee_combat[other]
