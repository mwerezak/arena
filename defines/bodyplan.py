
from core.creature.bodyplan import (
    Morphology, BodyElement, BodyElementType,
    BodyElementPlacement as Placement,
    BodyPartFlag,
)

## 'generic' Morphologies that can be used by different species

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

STANDARD_QUADRUPED = (
    Morphology(STANDARD_4LIMBS)
    .select('head')
    .set(
        name      = 'Head and Neck',
        size      = 2,
        placement = Placement.FORE,
        flags     = BodyPartFlag.VITAL,
    )
    .select('ubody')
    .set(
        name      = 'Forequarters',
        size      = 3,
        placement = Placement.MEDIAL | Placement.FORE,
        flags     = BodyPartFlag.VITAL,
    )
    .select('l_arm')
    .set(
        name      = 'Left Front Leg',
        size      = 2,
        placement = Placement.FORE | Placement.LEFT,
        flags     = BodyPartFlag.STANCE,
    )
    .select('r_arm')
    .set(
        name      = 'Right Front Leg',
        size      = 2,
        placement = Placement.FORE | Placement.RIGHT,
        flags     = BodyPartFlag.STANCE,
    )
    .select('lbody')
    .set(
        name      = 'Hindquarters',
        size      = 3,
        placement = Placement.MEDIAL | Placement.REAR,
        flags     = BodyPartFlag.VITAL,
    )
    .select('l_leg')
    .set(
        name      = 'Left Rear Leg',
        size      = 2,
        placement = Placement.REAR | Placement.LEFT,
        flags     = BodyPartFlag.STANCE,
    )
    .select('r_leg')
    .set(
        name      = 'Right Rear Leg',
        size      = 2,
        placement = Placement.REAR | Placement.RIGHT,
        flags     = BodyPartFlag.STANCE,
    )
    .select('tail')
    .set(
        name      = 'Tail',
        size      = 1,
        placement = Placement.REAR,
    )
    .finalize()
)

QUADRUPED_UNGULATE = (
    Morphology(STANDARD_QUADRUPED)
    .select('l_leg', 'r_leg')
    .set(size = 3)
    .select('tail')
    .set(size = 0.5)
    .finalize()
)

QUADRUPED_PACHYDERM = (
    Morphology(QUADRUPED_UNGULATE)
    .add(BodyElement('trunk', BodyElementType.LIMB,
        name      = 'trunk',
        size      = 1,
        placement = Placement.FORE,
        flags     = BodyPartFlag.GRASP,
    ))
    .finalize()
)

QUADRUPED_CANIFORME = (
    Morphology(STANDARD_QUADRUPED)
    .finalize()
)


STANDARD_HUMANOID = (
    Morphology(STANDARD_4LIMBS)
    .select('head')
    .set(
        name     = 'Head and Neck',
        size     = 2,
        flags    = BodyPartFlag.VITAL,
    )
    .select('ubody')
    .set(
        name      = 'Chest',
        size      = 3,
        flags     = BodyPartFlag.VITAL,
    )
    .select('l_arm')
    .set(
        name      = 'Left Arm',
        size      = 2,
        placement = Placement.CENTRAL | Placement.LEFT,
        flags     = BodyPartFlag.GRASP,
    )
    .select('r_arm')
    .set(
        name      = 'Right Arm',
        size      = 2,
        placement = Placement.CENTRAL | Placement.RIGHT,
        flags     = BodyPartFlag.GRASP,
    )
    .select('lbody')
    .set(
        name      = 'Lower Body',
        size      = 3,
        flags     = BodyPartFlag.VITAL,
    )
    .select('l_leg')
    .set(
        name      = 'Left Leg',
        size      = 2,
        placement = Placement.CENTRAL | Placement.LEFT,
        flags     = BodyPartFlag.STANCE,
    )
    .select('r_leg')
    .set(
        name = 'Right Leg',
        size      = 2,
        placement = Placement.CENTRAL | Placement.RIGHT,
        flags     = BodyPartFlag.STANCE,
    )
    .select('tail')
    .set(
        name      = 'Tail',
        size      = 1,
        placement = Placement.REAR,
    )
    .finalize()
)

HUMANOID_NOTAIL = (
    Morphology(STANDARD_HUMANOID)
        .select('tail')
        .remove()
        .finalize()
)

STANDARD_SERPENTINE = (
    Morphology([
        BodyElement('head',  BodyElementType.HEAD,      name='Head'            ),
        BodyElement('fore1', BodyElementType.UPPERBODY, name='Neck'            ),
        BodyElement('fore2', BodyElementType.UPPERBODY, name='Mid Fore-Length' ),
        BodyElement('fore3', BodyElementType.UPPERBODY, name='Rear Fore-length'),
        BodyElement('mid1',  BodyElementType.LOWERBODY, name='Fore Mid-Length' ),
        BodyElement('mid2',  BodyElementType.LOWERBODY, name='Mid Mid-Length'  ),
        BodyElement('mid3',  BodyElementType.LOWERBODY, name='Rear Mid-Length' ),
        BodyElement('rear1', BodyElementType.LIMB,      name='Fore Rear-Length'),
        BodyElement('rear2', BodyElementType.LIMB,      name='Mid Rear-Length' ),
        BodyElement('rear3', BodyElementType.LIMB,      name='Rear Rear-Length'),
        BodyElement('tail',  BodyElementType.LIMB,      name='Tail Tip'        ),
    ])
    .select('head')
    .set(
        size      = 2,
        placement = Placement.FORE,
        flags     = BodyPartFlag.VITAL,
    )
    .select('fore1', 'fore2', 'fore3')
    .set(
        size      = 3,
        placement = Placement.MEDIAL | Placement.FORE,
        flags     = BodyPartFlag.VITAL | BodyPartFlag.STANCE,
    )
    .select('mid1', 'mid2', 'mid3')
    .set(
        size      = 3,
        placement = Placement.MEDIAL,
        flags     = BodyPartFlag.VITAL | BodyPartFlag.STANCE,
    )
    .select('rear1', 'rear2', 'rear3')
    .set(
        size      = 2,
        placement = Placement.MEDIAL | Placement.REAR,
        flags     = BodyPartFlag.STANCE,
    )
    .select('tail')
    .set(
        size      = 1,
        placement = Placement.REAR,
    )
    .finalize()
)
