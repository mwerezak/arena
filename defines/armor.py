from core.armor import ArmorType, ArmorMaterial, MaterialType, ArmorTemplate

ARMORTYPE_HIDE       = ArmorType(1, 2.0,   20, 0.20, [MaterialType.Leather, MaterialType.Cloth])  # e.g. furs, hides
ARMORTYPE_PADDED     = ArmorType(2, 1.0,   80, 0.15, [MaterialType.Leather, MaterialType.Cloth])  # aketon, gambeson
ARMORTYPE_LAMINATED  = ArmorType(3, 2.0,  180, 0.10, [MaterialType.Leather, MaterialType.Cloth, MaterialType.Mineral])  # linothorax, bezainted
ARMORTYPE_SCALED     = ArmorType(4, 3.0,  320, 0.10, [MaterialType.Leather, MaterialType.Metal, MaterialType.Mineral])  # scale mail, lamellar, brigandine
ARMORTYPE_HALF_PLATE = ArmorType(5, 4.0,  500, 0.10, [MaterialType.Leather, MaterialType.Metal, MaterialType.Mineral])  # hoplite plate - non-fitted plates
ARMORTYPE_MAIL       = ArmorType(6, 5.0,  900, 0.10, [MaterialType.Metal])  # chainmail, laminar (banded mail)
ARMORTYPE_PLATE_MAIL = ArmorType(7, 6.0, 1400, 0.05, [MaterialType.Metal])  # splinted chainmail, coat of plates
ARMORTYPE_FULL_PLATE = ArmorType(8, 7.0, 2400, 0.01, [MaterialType.Metal])  # gothic plate

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

## Armor Templates

PATTERN_HELMET  = ['head']
PATTERN_CUIRASS = ['ubody', 'lbody']
PATTERN_ARMOR   = ['ubody', 'lbody', 'l_arm', 'r_arm']
PATTERN_HAUBERK = ['ubody', 'lbody', 'l_leg', 'r_leg']
PATTERN_SUIT    = ['ubody', 'lbody', 'l_arm', 'r_arm', 'l_leg', 'r_leg']

GAMBESON = ArmorTemplate('Gambeson', ARMORTYPE_PADDED, MATERIAL_LINEN, PATTERN_SUIT)
LEATHER_CUIRASS = ArmorTemplate('Cuirass', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_CUIRASS)
STEEL_BRIGANDINE_CUIRASS = ArmorTemplate('Brigandine Cuirass', ARMORTYPE_SCALED, MATERIAL_STEEL, PATTERN_CUIRASS)

STEEL_HALF_PLATE_CUIRASS = ArmorTemplate('Breastplate', ARMORTYPE_HALF_PLATE, MATERIAL_STEEL, PATTERN_CUIRASS)
STEEL_HALF_PLATE_ARMOR   = ArmorTemplate('Half-Plate Armor (Half-Suit)', ARMORTYPE_HALF_PLATE, MATERIAL_STEEL, PATTERN_ARMOR)

STEEL_PLATE_MAIL_ARMOR   = ArmorTemplate('Splinted Plate Armor (Half-Suit)', ARMORTYPE_PLATE_MAIL, MATERIAL_STEEL, PATTERN_ARMOR)

LEATHER_CAP    = [('head', ARMORTYPE_PADDED, MATERIAL_LEATHER)]
LEATHER_HELMET = [('head', ARMORTYPE_LAMINATED, MATERIAL_LEATHER)]
STEEL_HELMET   = [('head', ARMORTYPE_SCALED, MATERIAL_STEEL)]
