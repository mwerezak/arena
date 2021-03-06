from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, MutableSequence, Optional, Iterable, Type, Tuple, Any, Collection

from core.constants import Stance
from core.contest import OpposedResult, UnopposedResult, ContestResult, DifficultyGrade, ContestModifier, SKILL_EVADE, SKILL_ACROBATICS
from core.combat.criticals import DEFAULT_CRITICALS, CriticalUsage
from core.combat.damage import DamageType
from core.creature.traits import EvadeTrait

if TYPE_CHECKING:
    from core.dice import DicePool
    from core.constants import AttackForce
    from core.creature import Creature
    from core.creature.bodypart import BodyPart
    from core.combat.melee import MeleeCombat, MeleeRange
    from core.combat.attack import MeleeAttack
    from core.combat.criticals import CriticalEffect

def get_parry_damage_mult(attack_force: AttackForce, defend_force: AttackForce) -> float:
    if defend_force < attack_force.get_step(-1):
        return 1.0
    if defend_force < attack_force:
        return 0.5
    return 0

def get_random_hitloc(creature: Creature) -> Optional[BodyPart]:
    bodyparts = [ (bp, bp.exposure) for bp in creature.get_bodyparts() ]
    result = random.choices(*zip(*bodyparts))
    if len(result) > 0:
        return result[0]
    return None

# affects attack, parry, and evade, but not blocking
def get_combat_difficulty(creature: Creature) -> DifficultyGrade:
    grade = DifficultyGrade.Standard
    if creature.stance == Stance.Crouching:
        grade = DifficultyGrade.Hard
    elif creature.stance == Stance.Prone:
        grade = DifficultyGrade.Formidable

    if creature.is_seriously_wounded():
        grade = grade.get_step(+1)

    return grade

def get_block_difficulty(creature: Creature) -> DifficultyGrade:
    grade = DifficultyGrade.Standard
    if creature.is_seriously_wounded():
        grade = grade.get_step(+1)
    return grade

class MeleeCombatResolver:
    melee: MeleeCombat
    damage: DicePool
    armpen: DicePool

    def __init__(self,
                 attacker: Creature,
                 defender: Creature,
                 use_attack: MeleeAttack = None,
                 use_defence: MeleeAttack = None,
                 used_sources: Collection[Any] = None):

        self.attacker = attacker
        self.defender = defender
        self.use_attack = use_attack
        self.use_defence = use_defence

        self.primary_result = None
        self.attacker_crit = 0
        self.defender_crit = 0
        self.is_blocking = False

        self.damage_mult: float = 0
        self.hitloc: Optional[BodyPart] = None

        # attacks and blocks can only be used once per attack resolution - this mainly affects secondary attacks
        if used_sources is not None:
            self.used_sources = used_sources
        else:
            self.used_sources = [ *self._get_standing_bodyparts(attacker), *self._get_standing_bodyparts(defender) ]

        self.seconary_attacks: MutableSequence[MeleeCombatResolver] = []

    # prevent creatures from kicking with all their legs in one attack resolution
    @staticmethod
    def _get_standing_bodyparts(creature: Creature) -> Iterable[BodyPart]:
        if creature.stance == Stance.Prone:
            return ()

        current, total = creature.get_stance_count()
        used = total
        if creature.stance == Stance.Crouching:
            used = int(total / 2)
        elif creature.stance == Stance.Standing:
            used = min(total / 2 + 1, total - 1)
        used = min(used, current)

        stance_parts = list(bp for bp in creature.get_bodyparts() if bp.is_stance_part())
        return random.sample(stance_parts, used)

    @property
    def attack_result(self) -> ContestResult:
        return self.primary_result.pro_result

    @property
    def melee(self) -> Optional[MeleeCombat]:
        return self.attacker.get_melee_combat(self.defender)

    @property
    def separation(self) -> MeleeRange:
        return self.melee.get_separation()

    def is_effective_hit(self) -> bool:
        return self.damage_mult > 0 and self.damage.max() > 0

    def add_secondary_attack(self, attacker: Creature, defender: Creature, use_attack: MeleeAttack):
        secondary = MeleeCombatResolver(attacker, defender, use_attack, used_sources=self.used_sources)
        self.used_sources.append(use_attack.source)
        self.seconary_attacks.append(secondary)

    def generate_attack_results(self, *, opportunity_attack: bool = False, force_nodefence: bool = False) -> bool:
        if self.melee is None:
            return False

        # Choose Attack
        if self.use_attack is None or not self.use_attack.can_attack(self.separation):
            attacks = (attack for attack in self.attacker.get_melee_attacks() if attack.source not in self.used_sources)
            self.use_attack = self.attacker.mind.get_melee_attack(self.defender, self.separation, attacks)
        if self.use_attack is None or not self.use_attack.can_attack(self.separation):
            return False # no attack happens

        if opportunity_attack:
            self._resolve_melee_evade()
            return True
        if force_nodefence:
            self._resolve_melee_nodefence()
            return True

        # Choose Defence
        if self.use_defence is None or not self.use_defence.can_defend(self.separation):
            defence = (defence for defence in self.defender.get_melee_attacks() if defence.source not in self.used_sources)
            self.use_defence = self.defender.mind.get_melee_defence(self.attacker, self.use_attack, self.separation, defence)
        if self.use_defence is None or not self.use_defence.can_defend(self.separation):
            self._resolve_melee_nodefence()
            return True

        self._resolve_melee_defence()
        return True

    def _resolve_melee_defence(self) -> None:
        attack_modifier = get_combat_difficulty(self.attacker).to_modifier()
        defend_modifier = get_combat_difficulty(self.defender).to_modifier()

        attack_result = ContestResult(self.attacker, self.use_attack.combat_test, attack_modifier)
        defend_result = ContestResult(self.defender, self.use_defence.combat_test, defend_modifier)
        primary_result = OpposedResult(attack_result, defend_result)

        print(f'{self.attacker} attacks {self.defender} at {self.separation} distance: {self.use_attack.name} vs {self.use_defence.name}!')
        print(primary_result.format_details())

        damage_mult = 1.0
        if not primary_result.success:
            damage_mult = get_parry_damage_mult(self.use_attack.force, self.use_defence.force)

        # defender may attempt to block
        is_blocking, damage_mult = self._resolve_shield_block(attack_result, damage_mult)

        self.attacker_crit = 0
        self.defender_crit = 0
        if primary_result.success:
            self.attacker_crit = primary_result.crit_level
        else:
            self.defender_crit = primary_result.crit_level

        hitloc = None
        if damage_mult > 0:
            hitloc = get_random_hitloc(self.defender)

        self.primary_result = primary_result
        self.is_blocking = is_blocking
        self.hitloc = hitloc
        self.damage_mult = damage_mult
        self.damage = self.use_attack.damage
        self.armpen = self.use_attack.armpen
        self.used_sources.append(self.use_attack.source)
        self.used_sources.append(self.use_defence.source)

    def _resolve_melee_evade(self) -> None:
        attack_modifier = get_combat_difficulty(self.attacker).to_modifier()
        evade_modifier = get_combat_difficulty(self.defender).to_modifier()

        attack_result = ContestResult(self.attacker, self.use_attack.combat_test, attack_modifier)
        evade_result = ContestResult(self.defender, SKILL_EVADE, evade_modifier)
        primary_result = OpposedResult(attack_result, evade_result)

        print(f'{self.attacker} attacks {self.defender} at {self.separation} distance: {self.use_attack.name} vs {SKILL_EVADE}!')
        print(primary_result.format_details())

        damage_mult = 1.0 if primary_result.success else 0.0

        # defender may attempt to block
        is_blocking = False
        if primary_result.success:
            is_blocking, damage_mult = self._resolve_shield_block(attack_result, damage_mult)

        self.attacker_crit = primary_result.crit_level if primary_result.success else 0
        self.defender_crit = 0

        hitloc = None
        if damage_mult > 0:
            hitloc = get_random_hitloc(self.defender)

        self.primary_result = primary_result
        self.is_blocking = is_blocking
        self.hitloc = hitloc
        self.damage_mult = damage_mult
        self.damage = self.use_attack.damage
        self.armpen = self.use_attack.armpen
        self.used_sources.append(self.use_attack.source)

    def _resolve_melee_nodefence(self) -> None:
        if self.defender.has_trait(EvadeTrait):
            self._resolve_melee_evade()
            return

        attack_modifier = get_combat_difficulty(self.attacker).get_step(-1).to_modifier()
        attack_target = UnopposedResult.DEFAULT_TARGET + get_combat_difficulty(self.defender).contest_mod

        attack_result = ContestResult(self.attacker, self.use_attack.combat_test, attack_modifier)
        primary_result = UnopposedResult(attack_result, attack_target)
        print(f'{self.attacker} attacks {self.defender} at {self.separation} distance: {self.use_attack.name} vs no defence!')
        print(primary_result.format_details())

        damage_mult = 1.0 if primary_result.success else 0.0

        # defender may attempt to block
        is_blocking = False
        if primary_result.success:
            is_blocking, damage_mult = self._resolve_shield_block(attack_result, damage_mult)

        # if the attacker succeeds, they always get at least 1 critical effect
        self.attacker_crit = primary_result.crit_level if primary_result.success else 0
        self.defender_crit = 0

        hitloc = None
        if damage_mult > 0:
            hitloc = get_random_hitloc(self.defender)

        self.primary_result = primary_result
        self.is_blocking = is_blocking
        self.hitloc = hitloc
        self.damage_mult = damage_mult
        self.damage = self.use_attack.damage
        self.armpen = self.use_attack.armpen
        self.used_sources.append(self.use_attack.source)

    def _resolve_shield_block(self, attack_result: ContestResult, damage_mult: float) -> Tuple[bool, float]:
        blocks = (block for block in self.defender.get_shield_blocks() if block.source not in self.used_sources)
        self.use_shield = self.defender.mind.get_melee_block(self.separation, blocks)
        if self.use_shield is not None and self.use_shield.can_block(self.separation):
            block_damage_mult = get_parry_damage_mult(self.use_attack.force, self.use_shield.force)
            if block_damage_mult < damage_mult:
                modifier = get_block_difficulty(self.defender).to_modifier() + self.use_shield.contest_modifier
                shield_result = ContestResult(self.defender, self.use_shield.combat_test, modifier)
                block_result = OpposedResult(shield_result, attack_result)

                print(f'{self.defender} attempts to block with {self.use_shield.source}!')
                print(block_result.format_details())

                self.used_sources.append(self.use_shield.source)
                if block_result.success:
                    return True, block_damage_mult

        return False, damage_mult

    def _resolve_evade_knockdown(self):
        if self.defender.stance > Stance.Prone:
            acro_test = ContestResult(self.defender, SKILL_ACROBATICS, self.defender.get_resist_knockdown_modifier())
            acro_result = OpposedResult(acro_test, self.attack_result)
            print(acro_result.format_details())
            if not acro_result.success:
                self.defender.knock_down()

    def resolve_critical_effects(self) -> None:
        if self.attacker_crit > 0:
            crit_usage = CriticalUsage.Offensive|CriticalUsage.Melee
            criticals = list(DEFAULT_CRITICALS)
            criticals.extend(self.use_attack.get_criticals())
            criticals = set(crit for crit in criticals if crit_usage in crit.usage)
            for i in range(self.attacker_crit):
                if not self._apply_critical_effect(self.attacker, crit_usage, criticals):
                    break

        if self.defender_crit > 0:
            crit_usage = CriticalUsage.Defensive|CriticalUsage.Melee
            criticals = list(DEFAULT_CRITICALS)
            criticals.extend(self.use_defence.get_criticals())
            criticals = set(crit for crit in criticals if crit_usage in crit.usage)
            for i in range(self.defender_crit):
                if not self._apply_critical_effect(self.defender, crit_usage, criticals):
                    break

    def _apply_critical_effect(self,
                               user: Creature,
                               usage: CriticalUsage,
                               criticals: Iterable[Type[CriticalEffect]]) -> bool:

        choices = [ c for crit in criticals if (c := crit(user, self, usage)).can_use() ]

        if len(choices) > 0:
            #print([c.name for c in choices])
            crit = random.choices(choices, [c.weight for c in choices])[0]

            print(f'({user}) !Critical Effect - {crit}!')
            crit.apply()
            return True
        return False

    def resolve_damage(self) -> None:
        if self.hitloc is None:
            return
        if self.damage_mult <= 0:
            return

        damage = self.damage.get_roll_result() * self.damage_mult
        armpen = self.armpen.get_roll_result() * self.damage_mult

        if armpen > 0:
            dam_text = f'{damage:.0f}/{armpen:.0f}*'
        else:
            dam_text = f'{damage:.0f}'

        mult_text = f' (x{self.damage_mult:.1f})' if self.damage_mult != 1.0 else ''
        print(f'{self.attacker} strikes {self.defender} in the {self.hitloc} for {dam_text} damage{mult_text}: {self.use_attack.name}!')

        wounds = self.hitloc.apply_damage(damage, armpen, self.attack_result)

        # knockdown due to damage
        self._resolve_knockdown((damage + wounds)/2)  # blocked damage is only counted as half for knockdown

    def _resolve_knockdown(self, damage: float) -> None:
        knockdown_threshold = self.defender.size
        if self.use_attack.damtype == DamageType.Bludgeon:
            knockdown_threshold = self.defender.size * 2/3
        elif self.use_attack.damtype == DamageType.Puncture:
            knockdown_threshold = self.defender.size * 3/2

        if self.defender.stance > Stance.Prone and damage >= knockdown_threshold:
            if damage >= float(self.defender.size):
                modifier = int(float(self.defender.size) - damage)
            else:
                modifier = DifficultyGrade.Easy.contest_mod

            modifier = ContestModifier(modifier) + self.defender.get_resist_knockdown_modifier()

            acro_result = ContestResult(self.defender, SKILL_ACROBATICS, modifier)
            test_result = UnopposedResult(acro_result)
            print(test_result.format_details())
            if not test_result.success:
                self.defender.knock_down()

    def resolve_secondary_attacks(self) -> None:
        resolved = []
        for secondary in self.seconary_attacks:
            if secondary.generate_attack_results():
                secondary.resolve_critical_effects()
                secondary.resolve_damage()
                resolved.append(secondary)

        for secondary in resolved:
            secondary.resolve_secondary_attacks()
