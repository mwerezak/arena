from __future__ import annotations

import math
from typing import TYPE_CHECKING, Iterable, Type, Mapping, Optional, Union, Any, Sequence, Tuple

from core.combat.attacktraits import NaturalWeaponTrait, AttackTrait
from core.dice import dice
from core.combat.attack import MeleeAttackTemplate
from core.constants import MeleeRange, SizeCategory, FORCE_MEDIUM
from core.combat.damage import DamageType
from core.contest import CombatSkillClass

if TYPE_CHECKING:
    from core.creature.template import CreatureTemplate
    from core.combat.criticals import CriticalEffect

def _create_table(table_data: Mapping[float, Any]) -> Sequence[Tuple[float, Any]]:
    return [(k,v) for k,v in sorted(table_data.items())]

_DAMAGE_TABLE = _create_table({
      0 : dice(0),
      1 : dice(1),
      2 : dice(1,2),
      4 : dice(1,3),
      8 : dice(1,4), # medium size
     16 : dice(1,6),
     24 : dice(1,8),
     32 : dice(1,10),
     40 : dice(1,12),
     48 : dice(1,10) + dice(1,3),
     56 : dice(1,12) + dice(1,3),
     64 : dice(1,8)  + dice(2,4),
     72 : dice(1,10) + dice(2,4),
     80 : dice(1,12) + dice(2,4),
     88 : dice(1,10) + dice(2,6),
     96 : dice(1,12) + dice(2,6),
    104 : dice(1,10) + dice(2,8),
    112 : dice(1,12) + dice(2,8),
    120 : dice(2,8)  + dice(3,4),
    128 : dice(5,6),
})

_ARMOR_PEN_TABLE = _create_table({
      0 : None,
      1 : -dice(1,8),
      2 : -dice(1,6),
      4 : -dice(1,4),
      8 : -dice(1,3),
     16 : -dice(1),
     24 : dice(0),
     32 : dice(1),
     40 : dice(1,3),
     48 : dice(1,4),
     56 : dice(1,6),
     64 : dice(1,8),
     72 : dice(1,10),
     80 : dice(1,12),
     88 : dice(1,10) + dice(1,3),
     96 : dice(1,12) + dice(1,3),
    104 : dice(1,8)  + dice(2,4),
    112 : dice(1,10) + dice(2,4),
    120 : dice(1,12) + dice(2,4),
    128 : dice(1,10) + dice(2,6),
})

def _table_lookup(table: Sequence[Tuple[float, Any]], key: float, shift: int = 0) -> Any:
    _, idx = min( (abs(key - pair[0]), idx) for idx, pair in enumerate(table) )
    _, result = table[ max(0, min(idx + shift, len(table) - 1)) ]
    return result

## min,max reach at Medium size
BASE_MAX_REACH = 1.0   # REACH_SHORT
BASE_MIN_REACH = 1.0/3 # REACH_CLOSE

class NaturalWeaponTemplate:
    def __init__(self,
                 name: str, damtype: DamageType,
                 force: float = 0, reach: float = 0,
                 damage: float = 0, armpen: Optional[float] = None,
                 criticals: Iterable[Type[CriticalEffect]] = (),
                 traits: Iterable[AttackTrait] = ()):

        self.name = name
        self.damtype = damtype
        self.reach = reach
        self.force = force  # affects both damage and armor penetration as well
        self.damage = damage
        self.armpen = armpen
        self.criticals = tuple(criticals)
        self.traits = (NaturalWeaponTrait(), *traits)

class NaturalWeapon:
    def __init__(self,
                 template: Union[NaturalWeapon, NaturalWeaponTemplate],
                 name: str = None,
                 force: float = 0, reach: float = 0,
                 damage: float = 0, armpen: Optional[float] = None,
                 criticals: Iterable[Type[CriticalEffect]] = (),
                 traits: Iterable[AttackTrait] = ()):

        if hasattr(template, 'as_template'):
            template = template.as_template()

        self.name = name or template.name
        self.damtype = template.damtype

        self.criticals = list(template.criticals)
        self.criticals.extend(criticals)

        self.traits = list(template.traits)
        self.traits.extend(traits)

        self.reach = template.reach + reach
        self.force = template.force + force  # affects both damage and armor penetration as well
        self.damage = template.damage + damage

        self.armpen = None
        if template.armpen is not None or (armpen is not None and armpen >= 0): # reducing armpen on a weapon that does not have armpen should not grant it
            self.armpen = (template.armpen or 0) + (armpen or 0)

    def as_template(self) -> NaturalWeaponTemplate:
        return NaturalWeaponTemplate(
            self.name, self.damtype, self.force, self.reach, self.damage, self.armpen, self.criticals
        )

    def create_attack(self, creature: CreatureTemplate) -> MeleeAttackTemplate:
        rel_size = creature.size/SizeCategory.Medium.to_size()

        max_reach = BASE_MAX_REACH * rel_size + self.reach
        min_reach = BASE_MIN_REACH * rel_size + self.reach

        force = FORCE_MEDIUM.get_step(round(math.log2(rel_size) + self.force))

        damage = _table_lookup(_DAMAGE_TABLE, float(creature.size), self.damage + self.force)

        armor_pen = None
        if self.damtype == DamageType.Bludgeon or self.armpen is not None:
            armor_pen = _table_lookup(_ARMOR_PEN_TABLE, float(creature.size), (self.armpen or 0) + self.force)

        return MeleeAttackTemplate(
            name = self.name,
            reach = (MeleeRange(round(max_reach)), MeleeRange(round(min_reach))),
            force = force,
            damtype = self.damtype,
            damage = damage,
            armpen = armor_pen,
            skill_class = CombatSkillClass.Unarmed,
            criticals = self.criticals,
            traits = self.traits,
        )


# class HardenedNaturalTrait(AttackTrait):
#     name = 'Formidable Natural Weapon'
#     desc = (
#         'This attack may be used to avoid damage when defending in melee combat, '
#         'even if the defender does not posses the Martial Artist trait. '
#     )
# HardenedNaturalTrait = HardenedNaturalTrait()