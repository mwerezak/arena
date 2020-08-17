from __future__ import annotations

import random
from typing import TYPE_CHECKING, MutableSequence, Optional, Iterable, Type, Tuple

from core.constants import Stance
from core.contest import OpposedResult, ContestResult, SKILL_EVADE, DifficultyGrade, ContestModifier
from core.combat.criticals import DEFAULT_CRITICALS, CriticalUsage

if TYPE_CHECKING:
    from core.dice import DicePool
    from core.constants import AttackForce
    from core.creature import Creature
    from core.creature.bodypart import BodyPart
    from core.combat.melee import MeleeCombat
    from core.combat.attack import MeleeAttack
    from core.combat.criticals import CriticalEffect

def get_parry_damage_mult(attack_force: AttackForce, defend_force: AttackForce) -> float:
    if defend_force < attack_force.get_step(-1):
        return 1.0
    if defend_force < attack_force:
        return 0.5
    return 0

def get_random_hitloc(creature: Creature) -> Optional[BodyPart]:
    bodyparts = list(creature.get_bodyparts())
    weights = [ bp.exposure for bp in bodyparts ]
    result = random.choices(bodyparts, weights)
    if len(result) > 0:
        return result[0]
    return None

# affects attack and parry, but not blocking
def get_stance_modifier(creature: Creature) -> ContestModifier:
    grade = DifficultyGrade.Standard
    if creature.stance == Stance.Crouched:
        grade = DifficultyGrade.Hard
    elif creature.stance == Stance.Prone:
        grade = DifficultyGrade.Formidable
    return grade.to_modifier()

class MeleeCombatResolver:
    melee: MeleeCombat
    damage: DicePool
    armpen: DicePool

    def __init__(self,
                 attacker: Creature,
                 defender: Creature,
                 use_attack: MeleeAttack = None,
                 use_defence: MeleeAttack = None,
                 is_secondary: bool = False):

        self.attacker = attacker
        self.defender = defender
        self.use_attack = use_attack
        self.use_defence = use_defence
        self.use_shield = None

        self.attacker_crit = 0
        self.defender_crit = 0
        self.is_blocking = False

        self.damage_mult: float = 0
        self.hitloc: Optional[BodyPart] = None

        self.is_secondary = is_secondary
        self.seconary_attacks: MutableSequence[MeleeCombatResolver] = []

        # TODO
        self.allow_attacker_followup = True
        self.allow_defender_followup = False
        self.attacker_followup = False
        self.defender_followup = False

    def is_effective_hit(self) -> bool:
        return self.damage_mult > 0 and self.damage.max() > 0

    def add_secondary_attack(self, attacker: Creature, defender: Creature, use_attack: MeleeAttack):
        secondary = MeleeCombatResolver(attacker, defender, use_attack, is_secondary=True)
        self.seconary_attacks.append(secondary)

    # TODO collect log output to be accessed later instead of printing immediately
    def generate_attack_results(self, *, force_defenceless: bool = False, force_evade = False) -> bool:
        melee = self.attacker.get_melee_combat(self.defender)
        if melee is None:
            return False

        self.melee = melee
        separation = melee.get_separation()

        # Choose Attack
        if self.use_attack is None or not self.use_attack.can_attack(separation):
            self.use_attack = self.attacker.tactics.get_normal_attack(self.defender, separation)
        if self.use_attack is None or not self.use_attack.can_attack(separation):
            return False # no attack happens

        if force_defenceless and force_evade:
            pass  # todo allow one or the other
        if force_evade:
            self._resolve_melee_evade()
            return True
        if force_defenceless:
            self._resolve_defender_helpless()
            return True

        # Choose Defence
        if self.use_defence is None or not self.use_defence.can_defend(separation):
            self.use_defence = self.defender.tactics.get_melee_defence(self.attacker, self.use_attack, separation)
        if self.use_defence is None or not self.use_defence.can_defend(separation):
            print(repr(self.use_defence))
            self._resolve_defender_helpless()
            return True

        self._resolve_melee_defence()
        return True

    def _resolve_melee_defence(self) -> None:
        separation = self.melee.get_separation()

        attack_modifier = get_stance_modifier(self.attacker)
        defend_modifier = get_stance_modifier(self.defender)

        attack_result = ContestResult(self.attacker, self.use_attack.combat_test, attack_modifier)
        defend_result = ContestResult(self.defender, self.use_defence.combat_test, defend_modifier)
        primary_result = OpposedResult(attack_result, defend_result)

        print(f'{self.attacker} attacks {self.defender} at {separation} distance: {self.use_attack.name} vs {self.use_defence.name}!')
        print(primary_result.format_details())

        damage_mult = 1.0
        if not primary_result.success:
            damage_mult = get_parry_damage_mult(self.use_attack.force, self.use_defence.force)

        # defender may attempt to block
        is_blocking, damage_mult = self._resolve_shield_block(attack_result, damage_mult)

        # TODO defender may attempt to evade?

        self.attacker_crit = 0
        self.defender_crit = 0
        if primary_result.success:
            self.attacker_crit = primary_result.crit_level
        else:
            self.defender_crit = primary_result.crit_level

        hitloc = None
        if damage_mult > 0:
            hitloc = get_random_hitloc(self.defender)

        self.is_blocking = is_blocking
        self.hitloc = hitloc
        self.damage_mult = damage_mult
        self.damage = self.use_attack.damage
        self.armpen = self.use_attack.armpen

    def _resolve_melee_evade(self) -> None:
        separation = self.melee.get_separation()

        attack_modifier = get_stance_modifier(self.attacker)
        evade_modifier = get_stance_modifier(self.defender)

        attack_result = ContestResult(self.attacker, self.use_attack.combat_test, attack_modifier)
        evade_result = ContestResult(self.defender, SKILL_EVADE, evade_modifier)
        primary_result = OpposedResult(attack_result, evade_result)

        print(f'{self.attacker} attacks {self.defender} at {separation} distance: {self.use_attack.name} vs {SKILL_EVADE}!')
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

        self.is_blocking = is_blocking
        self.hitloc = hitloc
        self.damage_mult = damage_mult
        self.damage = self.use_attack.damage
        self.armpen = self.use_attack.armpen

    def _resolve_defender_helpless(self) -> None:
        separation = self.melee.get_separation()

        attack_modifier = get_stance_modifier(self.attacker)

        attack_result = ContestResult(self.attacker, self.use_attack.combat_test, attack_modifier)
        print(f'{self.attacker} attacks {self.defender} at {separation} distance: {self.use_attack.name}!')
        print(attack_result.format_details(10))

        # TODO defender may attempt to evade?

        is_blocking, damage_mult = self._resolve_shield_block(attack_result, 1.0)

        self.attacker_crit = max(attack_result.get_crit_level(10), 1)
        self.defender_crit = 0

        self.hitloc = get_random_hitloc(self.defender)
        self.is_blocking = is_blocking
        self.damage_mult = damage_mult
        self.damage = self.use_attack.damage
        self.armpen = self.use_attack.armpen
        self.is_blocking = False

    def _resolve_shield_block(self, attack_result: ContestResult, damage_mult: float) -> Tuple[bool, float]:
        separation = self.melee.get_separation()

        self.use_shield = self.defender.tactics.get_melee_shield(separation)
        if self.use_shield is not None and self.use_shield.shield.can_block(separation):
            block_damage_mult = get_parry_damage_mult(self.use_attack.force, self.use_shield.shield.block_force)
            if block_damage_mult < damage_mult:
                shield_result = ContestResult(self.defender, self.use_shield.combat_test, ContestModifier(self.use_shield.shield.block_bonus))
                block_result = OpposedResult(shield_result, attack_result)

                print(f'{self.defender} attempts to block with {self.use_shield}!')
                print(block_result.format_details())

                if block_result.success:
                    return True, block_damage_mult
        return False, damage_mult

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

        damage = round(self.damage.get_roll_result() * self.damage_mult)
        armpen = round(self.armpen.get_roll_result() * self.damage_mult)
        if armpen > 0:
            dam_text = f'{damage}/{armpen}* ({self.use_attack.damtype.format_type_code()})'
        else:
            dam_text = f'{damage} ({self.use_attack.damtype.format_type_code()})'

        mult_text = f' (x{self.damage_mult:.1f})' if self.damage_mult != 1.0 else ''

        print(f'{self.attacker} hits {self.defender} in the {self.hitloc} for {dam_text} damage{mult_text}: {self.use_attack.name}!')

        wound = self.hitloc.apply_damage(damage, armpen)
        if wound > 0:
            print(f'{self.defender} is wounded for {wound:.1f} damage (armour {self.hitloc.get_armor()}). Health: {round(self.defender.health)}/{self.defender.max_health}')
        else:
            print(f'The armor absorbs the blow (armour {self.hitloc.get_armor()}). Health: {round(self.defender.health)}/{self.defender.max_health}')

    def resolve_seconary_attacks(self) -> None:
        # secondary attacks are similar to primary attacks but do not get to resolve secondary attacks of their own
        for secondary in self.seconary_attacks:
            if secondary.generate_attack_results():
                secondary.resolve_critical_effects()
                secondary.resolve_damage()
