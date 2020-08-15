from __future__ import annotations
import math
from typing import TYPE_CHECKING, MutableMapping, Optional, Iterable, Any, Union

from core.action import Entity
from core.constants import MeleeRange, PrimaryAttribute, Stance
from core.creature.traits import SkillTrait
from core.creature.bodypart import BodyPart
from core.creature.inventory import Inventory
from core.creature.tactics import CombatTactics
from core.contest import DifficultyGrade, SkillLevel

if TYPE_CHECKING:
    from core.constants import CreatureSize
    from core.combat.attack import MeleeAttack
    from core.creature.combat import MeleeCombat
    from core.creature.template import CreatureTemplate
    from core.creature.bodyplan import Morphology
    from core.equipment import Equipment
    from core.contest import Contest
    from core.creature.traits import CreatureTrait

class Creature(Entity):
    health: float
    inventory: Inventory

    def __init__(self, template: CreatureTemplate, tactics: CombatTactics = None):
        self.template = template
        self.name = template.name
        self.tactics = tactics or CombatTactics(self)

        self.health = template.max_health
        self.stance = Stance.Standing
        self.alive = True

        self._bodyparts = { bp.id_tag : BodyPart(self, bp) for bp in template.bodyplan }
        self._traits = { trait.key : trait for trait in template.get_traits() }

        self._mount: Optional[Creature] = None
        self._melee_combat: MutableMapping[Creature, MeleeCombat] = {}

        self.inventory = Inventory(self, (bp for bp in self.get_bodyparts() if bp.is_grasp_part()))

        template.loadout.apply_loadout(self)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'

    def __str__(self) -> str:
        return self.name

    @property
    def size(self) -> CreatureSize:
        return self.template.size

    @property
    def bodyplan(self) -> Morphology:
        return self.template.bodyplan

    def get_bodypart(self, id_tag: str) -> BodyPart:
        return self._bodyparts[id_tag]

    def get_bodyparts(self) -> Iterable[BodyPart]:
        return iter(self._bodyparts.values())

    def get_attribute(self, attr: Union[str, PrimaryAttribute]) -> int:
        return self.template.get_attribute(attr)

    def get_encumbrance(self) -> float:
        return self.inventory.get_encumbrance_total()

    def _base_initiative(self) -> float:
        attr_modifer = self.get_attribute(PrimaryAttribute.INT) + self.get_attribute(PrimaryAttribute.DEX)
        return 20.0 + 2.0*attr_modifer

    def get_action_rate(self) -> float:
        action_points = self._base_initiative()/12.0
        return action_points/(1/0.6)

    def get_initiative_modifier(self) -> float:
        return self._base_initiative()/2.0 - (self.get_encumbrance())/5.0

    @property
    def tiebreaker_priority(self) -> float:
        return self.get_initiative_modifier()

    ## Traits

    def add_trait(self, trait: CreatureTrait) -> None:
        self._traits[trait.key] = trait

    def get_trait(self, key: Any) -> Optional[CreatureTrait]:
        return self._traits.get(key)

    def has_trait(self, key: Any) -> bool:
        return self.get_trait(key) is not None

    def get_skill_level(self, contest: Contest) -> SkillLevel:
        trait: Optional[SkillTrait] = self.get_trait((SkillTrait, contest))
        if trait is not None:
            return trait.level
        return SkillLevel(0)

    ## Melee Combat

    def get_unarmed_attacks(self) -> Iterable[MeleeAttack]:
        # equipped items occupy exactly one of the bodyparts used to hold them
        occupied = { item : bp for bp, item in self.inventory.get_equip_slots() if item is not None }
        occupied = set(occupied.values())
        for bp in self.get_bodyparts():
            if bp not in occupied:
                yield from bp.get_unarmed_attacks()

    def get_melee_attacks(self) -> Iterable[MeleeAttack]:
        yield from self.get_unarmed_attacks()
        for item in self.inventory.get_held_items():
            if item.is_weapon():
                using_hands = sum(1 for bp in self.inventory.get_item_held_by(item) if bp.can_use())
                yield from item.get_melee_attacks(self, using_hands, item)

    def get_held_shields(self) -> Iterable[Equipment]:
        for item in self.inventory.get_held_items():
            if item.is_weapon() and item.is_shield():
                yield item

    def get_melee_engage_distance(self) -> MeleeRange:
        attack_reach = (attack.max_reach for attack in self.get_melee_attacks())
        return max(attack_reach, default=MeleeRange(0))

    def get_melee_opponents(self) -> Iterable[Creature]:
        return iter(self._melee_combat.keys())

    def get_melee_combat(self, other: Creature) -> Optional[MeleeCombat]:
        return self._melee_combat.get(other, None)

    def add_melee_combat(self, other: Creature, melee: MeleeCombat) -> None:
        self._melee_combat[other] = melee

    def remove_melee_combat(self, other: Creature) -> None:
        if other in self._melee_combat:
            del self._melee_combat[other]

    ## Stance

    def change_stance(self, new_stance: Stance) -> None:
        max_stance = self.get_max_stance()
        self.stance = Stance(max(new_stance.value, max_stance))

    def get_stance_combat_modifier(self) -> int:
        if self.stance == Stance.Prone:
            return DifficultyGrade.Formidable
        if self.stance == Stance.Crouched:
            return DifficultyGrade.Hard
        return DifficultyGrade.Standard

    def get_max_stance(self) -> Stance:
        total_stance = 0
        cur_stance = 0
        for bp in self.get_bodyparts():
            if bp.is_stance_part():
                total_stance += 1
                if bp.can_use():
                    cur_stance += 1

        threshold = math.ceil(total_stance/2)
        if cur_stance > threshold:
            return Stance.Standing
        if cur_stance >= threshold:
            return Stance.Crouched
        return Stance.Prone

    def check_stance(self) -> None:
        max_stance = self.get_max_stance()
        if self.stance.value > max_stance.value:
            self.change_stance(max_stance)

    def take_damage(self, amount: float) -> None:
        self.health -= amount
        if self.health <= 0: # todo wounding system
            self.kill()

    @property
    def max_health(self) -> float:
        return self.template.max_health

    def kill(self) -> None:
        self.alive = False
        self.stance = Stance.Prone
        # for o in list(self.get_melee_opponents()):
        #     melee = self.get_melee_combat(o)
        #     melee.break_engagement()

