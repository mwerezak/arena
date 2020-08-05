
from core.bodyplan import Morphology, BodyElement, BodyElementType, BodyElementSpecial

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

HUMANOID = (
    Morphology(STANDARD_4LIMBS)
        .select('head')
        .set(
            name = 'Head and Neck',
            exposure = 2,
            specials = [BodyElementSpecial.VITAL],
        )
        .select('ubody')
        .set(
            name = 'Chest',
            exposure = 3,
            specials = [BodyElementSpecial.VITAL],
        )
        .select('l_arm')
        .set(
            name = 'Left Arm',
            exposure = 3,
            specials = [BodyElementSpecial.GRASP],
        )
        .select('r_arm')
        .set(
            name = 'Right Arm',
            exposure = 3,
            specials = [BodyElementSpecial.GRASP],
        )
        .select('l_leg')
        .set(
            name = 'Left Leg',
            exposure = 3,
            specials = [BodyElementSpecial.STANCE],
        )
        .select('r_leg')
        .set(
            name = 'Right Leg',
            exposure = 3,
            specials = [BodyElementSpecial.STANCE],
        )
        .select('tail')
        .set(
            name = 'Tail',
            exposure = 1,
        )
        .get_bodyplan()
)

HUMANOID_NOTAIL = (
    Morphology(HUMANOID)
        .select('tail')
        .remove()
        .get_bodyplan()
)