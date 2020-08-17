from __future__ import annotations
from typing import TYPE_CHECKING

from core.traits import Trait

if TYPE_CHECKING:
    pass

class AttackTrait(Trait):
    pass

class NaturalWeaponTrait(AttackTrait):
    name = 'Natural Weapon'
    desc = 'This attack is an unarmed attack'

class FormidableNatural(AttackTrait):
    name = 'Formidable Natural Weapon'
    desc = 'This attack does not have the usual parry restrictions of an unarmed attack'

class CannotDefendTrait(AttackTrait):
    name = 'Cannot Parry'
    desc = 'This attack cannot be used to parry in defence.'