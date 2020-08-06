
from core.bodyplan import (
    Morphology, BodyElement, BodyElementType,
    BodyElementPlacement as Placement,
    BodyElementSpecial as Special,
)

## "generic" Morphologies that can be used by different species

STANDARD_4LIMBS = Morphology([
    BodyElement('head',  BodyElementType.HEAD),
    BodyElement('ubody', BodyElementType.UPPERBODY),
    BodyElement('l_arm', BodyElementType.LIMB),
    BodyElement('r_arm', BodyElementType.LIMB),
    BodyElement('lbody', BodyElementType.LOWERBODY),
    BodyElement('l_leg', BodyElementType.LIMB),
    BodyElement('r_leg', BodyElementType.LIMB),
    BodyElement('tail',  BodyElementType.TAIL),
])

QUADRUPED_UNGULATE = (
    Morphology(STANDARD_4LIMBS)
        .select("head")
        .set(
            name      = "Head and Neck",
            exposure  = 2,
            placement = Placement.MEDIAL | Placement.FORE,
            specials  = [Special.VITAL],
        )
        .select("ubody")
        .set(
            name      = "Forequarters",
            base_hp   = 3,
            exposure  = 3,
            placement = Placement.MEDIAL | Placement.FORE,
            specials  = [Special.VITAL],
        )
        .select("l_arm")
        .set(
            name      = "Left Front Leg",
            exposure  = 2,
            placement = Placement.FORE | Placement.LEFT,
            specials  = [Special.STANCE],
        )
        .select("r_arm")
        .set(
            name      = "Right Front Leg",
            exposure  = 2,
            placement = Placement.FORE | Placement.RIGHT,
            specials  = [Special.STANCE],
        )
        .select("lbody")
        .set(
            name      = "Hindquarters",
            exposure  = 3,
            placement = Placement.MEDIAL | Placement.REAR,
            specials  = [Special.VITAL],
        )
        .select("l_leg")
        .set(
            name      = "Left Rear Leg",
            exposure  = 3,
            placement = Placement.REAR | Placement.LEFT,
            specials  = [Special.STANCE],
        )
        .select("r_leg")
        .set(
            name      = "Right Rear Leg",
            exposure  = 3,
            placement = Placement.REAR | Placement.RIGHT,
            specials  = [Special.STANCE],
        )
        .select("tail")
        .set(
            name      = "tail",
            exposure  =  0.5,
            placement = Placement.REAR,
        )
        .finalize()
)


HUMANOID = (
    Morphology(STANDARD_4LIMBS)
        .select('head')
        .set(
            name = 'Head and Neck',
            exposure = 2,
            specials = [Special.VITAL],
        )
        .select('ubody')
        .set(
            name = 'Chest',
            exposure = 3,
            placement = Placement.CENTRAL,
            specials = [Special.VITAL],
        )
        .select('l_arm')
        .set(
            name = 'Left Arm',
            exposure = 3,
            placement = Placement.CENTRAL | Placement.LEFT,
            specials = [Special.GRASP],
        )
        .select('r_arm')
        .set(
            name = 'Right Arm',
            exposure = 3,
            placement = Placement.CENTRAL | Placement.RIGHT,
            specials = [Special.GRASP],
        )
        .select("lbody")
        .set(
            name      = "Lower Body",
            exposure  = 3,
            placement = Placement.CENTRAL,
            specials  = [Special.VITAL],
        )
        .select('l_leg')
        .set(
            name = 'Left Leg',
            exposure = 3,
            placement = Placement.CENTRAL | Placement.LEFT,
            specials = [Special.STANCE],
        )
        .select('r_leg')
        .set(
            name = 'Right Leg',
            exposure = 3,
            placement = Placement.CENTRAL | Placement.RIGHT,
            specials = [Special.STANCE],
        )
        .select('tail')
        .set(
            name = 'Tail',
            exposure = 1,
            placement = Placement.REAR,
        )
        .finalize()
)


HUMANOID_NOTAIL = (
    Morphology(HUMANOID)
        .select('tail')
        .remove()
        .finalize()
)

