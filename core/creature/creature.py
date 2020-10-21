from __future__ import annotations
import math
from typing import TYPE_CHECKING, MutableMapping, Optional, Iterable, Any, Union, Set, Tuple

from core.action import Entity
from core.constants import MeleeRange, PrimaryAttribute, Stance
from core.creature.traits import SkillTrait
from core.creature.bodypart import BodyPart
from core.creature.inventory import Inventory
from core.creature.mind.combat import CreatureMind
from core.creature.actions import StunnedAction
from core.contest import (
    Contest, ContestResult, ContestModifier, DifficultyGrade, SkillLevel,
    OpposedResult, UnopposedResult, SKILL_RIDING, SKILL_ENDURANCE,
)

if TYPE_CHECKING:
    from core.constants import CreatureSize
    from core.combat.attack import MeleeAttack
    from core.combat.shield import ShieldBlock
    from core.combat.melee import MeleeCombat
    from core.creature.template import CreatureTemplate
    from core.creature.bodyplan import Morphology
    from core.creature.traits import CreatureTrait

class Creature(Entity):
    health: float
    inventory: Inventory

    def __init__(self, template: CreatureTemplate, mind: CreatureMind = None):
        self.template = template
        self.name = template.name
        self.mind = mind or CreatureMind(self)

        self._stance = Stance.Standing
        self._health = template.max_health
        self._conscious = True
        self._alive = True

        self._bodyparts = { bp.id_tag : BodyPart(self, bp) for bp in template.bodyplan }
        self._traits = { trait.key : trait for trait in template.get_traits() }

        self._mount: Optional[Creature] = None
        self._riders: Set[Creature] = set()

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
        if not self.is_conscious():
            return

        # equipped items occupy exactly one of the bodyparts used to hold them
        occupied = [bp for bp in self.inventory.get_equip_slots() if self.inventory.get_item_in_slot(bp) is not None]
        for bp in self.get_bodyparts():
            if not bp.can_use() or bp in occupied:
                continue
            if self.stance == Stance.Mounted and bp.is_stance_part():
                continue  # no kicking while mounted
            yield from bp.get_unarmed_attacks()

    def get_melee_attacks(self) -> Iterable[MeleeAttack]:
        if not self.is_conscious():
            return

        yield from self.get_unarmed_attacks()
        for item in self.inventory.get_held_items():
            if item.is_weapon():
                using_hands = sum(1 for bp in self.inventory.get_item_held_by(item) if bp.can_use())
                if using_hands > 0:
                    yield from item.get_melee_attacks(self, using_hands, item)

    def get_shield_blocks(self) -> Iterable[ShieldBlock]:
        if not self.is_conscious():
            return

        for item in self.inventory.get_held_items():
            if item.is_weapon() and item.is_shield():
                yield item.shield.create_instance(self, item)

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

    @property
    def stance(self) -> Stance:
        return self._stance

    def change_stance(self, new_stance: Stance) -> None:
        prev_stance = self._stance
        self._stance = min(max(self.min_stance, new_stance), self.max_stance)
        # if self._stance != prev_stance:
        #     print(f'{self} changes stance ({prev_stance} -> {self._stance}).')

    @property
    def min_stance(self) -> Stance:
        if self._mount is not None:
            return Stance.Mounted
        return Stance.Prone

    @property
    def max_stance(self) -> Stance:
        if self._mount is not None:
            return Stance.Mounted

        cur_stance, total_stance = self.get_stance_count()

        if cur_stance >= int(math.ceil(total_stance/2 + 0.5)):
            return Stance.Standing
        if cur_stance >= int(math.floor(total_stance/2)):
            return Stance.Crouching
        return Stance.Prone

    def get_stance_count(self) -> Tuple[int, int]:
        total_stance = 0
        cur_stance = 0
        for bp in self.get_bodyparts():
            if bp.is_stance_part():
                total_stance += 1
                if bp.can_use():
                    cur_stance += 1
        return cur_stance, total_stance

    _lost_stance_text = {
        Stance.Standing  : 'can no longer stand',
        Stance.Crouching : 'falls over'
    }
    def check_stance(self) -> None:
        if self.stance > self.max_stance:
            print(f'{self} {self._lost_stance_text[self.stance]}!')
            self.change_stance(self.max_stance)

    def get_resist_knockdown_modifier(self, difficulty_step: int = 0) -> ContestModifier:
        grade = DifficultyGrade.Standard
        if self.stance == Stance.Crouching or self.stance == Stance.Mounted:
            grade = DifficultyGrade.Easy
        grade = grade.get_step(difficulty_step)

        leg_count, leg_total = self.get_stance_count()
        return grade.to_modifier() + ContestModifier(leg_total - 2 + (leg_count - leg_total))

    def knock_down(self) -> None:
        if self._mount is not None:
            self.dismount()
        self.change_stance(Stance.Prone)
        print(f'{self} is knocked down!')

    ## Mounts

    def get_mount(self) -> Optional[Creature]:
        return self._mount

    def get_primary_rider(self) -> Optional[Creature]:
        return max(self.get_riders(), default=None, key=lambda c: c.get_skill_level(SKILL_RIDING))

    def get_riders(self) -> Iterable[Creature]:
        return iter(self._riders)

    def set_mount(self, mount: Optional[Creature]) -> None:
        if mount.get_mount() is not None:
            raise ValueError  # just... no

        if mount == self._mount:
            return
        if self._mount is not None:
            self.dismount()
        if mount is not None:
            self._mount = mount
            mount._riders.add(self)

    def dismount(self) -> None:
        if self._mount is not None:
            # noinspection PyProtectedMember
            self._mount._riders.remove(self)
        self._mount = None

    ## Damage and Health

    @property
    def health(self) -> float:
        return self._health

    @property
    def max_health(self) -> float:
        return self.template.max_health

    def is_conscious(self) -> bool:
        return self._conscious

    def set_conscious(self, value: bool) -> None:
        if value == self._conscious:
            return

        self._conscious = value
        if not self._conscious:
            self.dismount()
            self.change_stance(Stance.Prone)
            self.set_current_action(None)

    def is_alive(self) -> bool:
        return self._alive

    def is_seriously_wounded(self) -> bool:
        return self.health <= 0

    def apply_wounds(self, amount: float, bodypart: BodyPart, attack_result: Optional[ContestResult] = None) -> None:
        prev_health = self.health
        self._health -= amount

        if self.health <= 0 < prev_health:
            self.stun(can_defend=False)

        if self.health <= -self.max_health:
            # unlikely to die instantly if taking damage to a non-vital body part
            grade = DifficultyGrade.Standard if bodypart.is_vital() else DifficultyGrade.VeryEasy
            injury_test = ContestResult(self, SKILL_ENDURANCE, grade.to_modifier())
            injury_result = OpposedResult(injury_test, attack_result) if attack_result is not None else UnopposedResult(injury_test)

            print(injury_result.format_details())
            if not injury_result.success:
                self.kill()
                print(f'{self} is killed!')
            elif self.is_conscious():
                self.set_conscious(False)
                print(f'{self} is incapacitated!')

        elif self.health <= 0 and self.is_conscious():

            injury_test = ContestResult(self, SKILL_ENDURANCE)
            injury_result = OpposedResult(injury_test, attack_result) if attack_result is not None else UnopposedResult(injury_test)

            print(f'{self} is seriously wounded!')
            print(injury_result.format_details())
            if not injury_result.success:
                self.set_conscious(False)
                print(f'{self} is incapacitated!')

    def stun(self, can_defend: bool = True) -> None:
        action = self.get_current_action()
        if action is not None and action.is_resolving():
            action.set_force_next(StunnedAction(can_defend))
        else:
            self.set_current_action(StunnedAction(can_defend))

    def kill(self) -> None:
        self.set_conscious(False)
        self._alive = False


