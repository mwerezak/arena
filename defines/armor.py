from core.armor import ArmorType, ArmorMaterial, MaterialType

ARMOR_HIDE       = ArmorType(1, 2.0,   20, 0.20, [MaterialType.Leather, MaterialType.Cloth])  # e.g. furs, hides
ARMOR_PADDED     = ArmorType(2, 1.0,   80, 0.15, [MaterialType.Leather, MaterialType.Cloth])  # aketon, gambeson
ARMOR_LAMINATED  = ArmorType(3, 2.0,  180, 0.10, [MaterialType.Leather, MaterialType.Cloth, MaterialType.Mineral])  # linothorax, bezainted
ARMOR_SCALED     = ArmorType(4, 3.0,  320, 0.10, [MaterialType.Leather, MaterialType.Metal, MaterialType.Mineral])  # scale mail, lamellar, brigandine
ARMOR_HALF_PLATE = ArmorType(5, 4.0,  500, 0.10, [MaterialType.Leather, MaterialType.Metal, MaterialType.Mineral])  # hoplite plate - non-fitted plates
ARMOR_MAIL       = ArmorType(6, 5.0,  900, 0.10, [MaterialType.Metal])  # chainmail, laminar (banded mail)
ARMOR_PLATE_MAIL = ArmorType(7, 6.0, 1400, 0.05, [MaterialType.Metal])  # splinted chainmail, coat of plates
ARMOR_FULL_PLATE = ArmorType(8, 7.0, 2400, 0.01, [MaterialType.Metal])  # gothic plate

MATERIAL_BONE    = ArmorMaterial('Bone',     1.5,   0.75, MaterialType.Mineral)
MATERIAL_CHITIN  = ArmorMaterial('Chitin',   0.75,  1.5,  MaterialType.Mineral)
MATERIAL_IVORY   = ArmorMaterial('Ivory',    1.25,  0.8,  MaterialType.Mineral)
MATERIAL_SHELL   = ArmorMaterial('Shell',    2.0,   0.6,  MaterialType.Mineral)
MATERIAL_STONE   = ArmorMaterial('Obsidian', 3.0,   0.5,  MaterialType.Mineral)
MATERIAL_JADE    = ArmorMaterial('Jade',     3.0,   0.5,  MaterialType.Mineral)
MATERIAL_LEATHER = ArmorMaterial('Leather',  1.5,   0.75, MaterialType.Leather)
MATERIAL_LINEN   = ArmorMaterial('Linen',    1.0,   1.0,  MaterialType.Cloth)
MATERIAL_SILK    = ArmorMaterial('Silk',     0.75,  1.5,  MaterialType.Cloth)
MATERIAL_BRONZE  = ArmorMaterial('Bronze',   1.0,   1.0,  MaterialType.Metal)
MATERIAL_IRON    = ArmorMaterial('Iron',     1.0,   1.0,  MaterialType.Metal)
MATERIAL_STEEL   = ArmorMaterial('Steel',    0.75,  1.5,  MaterialType.Metal)

if __name__ == '__main__':
    from defines.bodyplan import *
    from core.creature import CreatureTemplate, SizeCategory
    from core.armor import Armor
    human = CreatureTemplate('Human', HUMANOID_NOTAIL, SizeCategory.Medium.value)

    armor = Armor('Cuirass', human, [
        ('ubody', ARMOR_HALF_PLATE, MATERIAL_LEATHER),
        ('lbody', ARMOR_HALF_PLATE, MATERIAL_LEATHER),
    ])

    helm = Armor('Helmet', human, [
        ('head', ARMOR_HALF_PLATE, MATERIAL_IRON),
    ])
