from __future__ import annotations

import random
from typing import TYPE_CHECKING, Sequence, Tuple, Optional, NamedTuple

from core.contest import OpposedResult, ContestResult
from core.creature import Creature
from core.equipment import Equipment

if TYPE_CHECKING:
    from core.dice import DicePool
    from core.constants import MeleeRange, AttackForce
    from core.creature.combat import MeleeCombat
    from core.combat.attack import MeleeAttackInstance

def can_opportunity_attack(combatant: Creature):
    cur_action = combatant.get_current_action()
    if cur_action is None:
        return True  # idle
    return getattr(cur_action, 'can_attack', True)

def get_defence_damage_mult(attack_force: AttackForce, defend_force: AttackForce) -> float:
    if defend_force < attack_force.get_step(-1):
        return 1.0
    if defend_force < attack_force:
        return 0.5
    return 0

def get_random_hitloc(creature: Creature) -> Optional[str]:
    bodyparts = ( (bp.id_tag, bp.size) for bp in creature.bodyplan )
    hitlocs, weights = zip(*bodyparts)
    result = random.choices(hitlocs, weights)
    if len(result) > 0:
        return result[0]
    return None

class CombatResult:
    def __init__(self,
                 melee: MeleeCombat,
                 use_attack: MeleeAttackInstance,
                 use_defence: MeleeAttackInstance,
                 is_hit: bool,
                 is_blocking: bool,
                 hitloc: Optional[str],
                 damage_mult: float,
                 damage: DicePool,
                 armpen: Optional[DicePool]):

        self.melee = melee
        self.use_attack = use_attack
        self.use_defence = use_defence
        self.is_hit = is_hit
        self.is_blocking = is_blocking
        self.hitloc = hitloc
        self.damage = damage
        self.damage_mult = damage_mult

    def is_effective_hit(self) -> bool:
        return self.damage_mult > 0 and self.damage.max() > 0

def resolve_melee_attack(attacker: Creature, defender: Creature) -> Optional[CombatResult]:
    combat_log = []

    melee = attacker.get_melee_combat(defender)

    use_attack = attacker.tactics.get_normal_attack(defender, melee.separation)
    if use_attack is None or not use_attack.can_reach(melee.separation):
        return None

    use_defence = defender.tactics.get_melee_defence(attacker, use_attack, melee.separation)
    if use_defence is None or not use_defence.can_defend(melee.separation):
        raise NotImplemented  # TODO defender helpless

    print(f'{attacker} attacks {defender}: {use_attack} vs {use_defence}!')
    attack_result = ContestResult(attacker, use_attack.combat_test)
    defend_result = ContestResult(defender, use_defence.combat_test)
    primary_result = OpposedResult(attack_result, defend_result)

    print(primary_result.format_details())

    damage_mult = 1.0
    if not primary_result.success:
        damage_mult = get_defence_damage_mult(use_attack.force, use_defence.force)

    # defender may attempt to block
    block_result = None
    is_blocking = False
    use_shield = defender.tactics.get_melee_shield()
    if use_shield is not None:
        block_damage_mult = get_defence_damage_mult(use_attack.force, use_shield.block.block_force)
        if block_damage_mult < damage_mult:
            combat_log.append(f'{defender} attempts to block with {use_shield}!')
            shield_result = ContestResult(defender, use_shield.combat_test)
            block_result = OpposedResult(attack_result, shield_result)
            if not block_result.success:
                is_blocking = True
                damage_mult = block_damage_mult

    attacker_crit = 0
    defender_crit = 0
    if primary_result.success:
        attacker_crit = primary_result.crit_level
    else:
        defender_crit = primary_result.crit_level

    hitloc = None
    if damage_mult > 0:
        hitloc = get_random_hitloc(defender)

    result = CombatResult(
        melee = melee,
        use_attack = use_attack,
        use_defence = use_defence,
        is_blocking = is_blocking,
        is_hit = primary_result.success,
        hitloc = hitloc,
        damage_mult = damage_mult,
        damage = use_attack.damage,
        armpen = use_attack.armpen,
    )

    # TODO defender may attempt to evade
    #if damage_mult > 0:
    #    damage =

