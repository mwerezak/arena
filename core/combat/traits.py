from __future__ import annotations
from typing import TYPE_CHECKING

from core.traits import Trait

if TYPE_CHECKING:
    pass

class AttackTrait(Trait):
    pass

class NaturalWeaponTrait(AttackTrait):
    name = 'Natural Weapon'
    desc = 'This attack is a natural weapon'
NaturalWeaponTrait = NaturalWeaponTrait()

class CannotDefendTrait(AttackTrait):
    name = 'Cannot Parry'
    desc = 'This attack cannot be used to parry in defence.'
CannotDefendTrait = CannotDefendTrait()