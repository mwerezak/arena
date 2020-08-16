from core.equipment.armor import ArmorType, ArmorMaterial, MaterialType, ArmorTemplate

ARMORTYPE_HIDE       = ArmorType(1, 2.0,   20, 0.20, [MaterialType.Leather, MaterialType.Cloth])  # e.g. furs, hides
ARMORTYPE_PADDED     = ArmorType(2, 1.0,   80, 0.15, [MaterialType.Leather, MaterialType.Cloth])  # aketon, gambeson
ARMORTYPE_LAMINATED  = ArmorType(3, 2.0,  180, 0.10, [MaterialType.Leather, MaterialType.Cloth, MaterialType.Mineral])  # linothorax, bezainted
ARMORTYPE_SCALED     = ArmorType(4, 3.0,  320, 0.10, [MaterialType.Leather, MaterialType.Metal, MaterialType.Mineral])  # scale mail, lamellar, brigandine
ARMORTYPE_HALF_PLATE = ArmorType(5, 4.0,  500, 0.10, [MaterialType.Leather, MaterialType.Metal, MaterialType.Mineral])  # hoplite plate - non-fitted plates
ARMORTYPE_MAIL       = ArmorType(6, 5.0,  900, 0.10, [MaterialType.Metal])  # chainmail, laminar (banded)
ARMORTYPE_BANDED     = ArmorType(6, 5.0,  900, 0.10, [MaterialType.Metal])  # laminar (banded)
ARMORTYPE_SPLINTED   = ArmorType(7, 6.0, 1400, 0.05, [MaterialType.Metal])  # splinted chainmail, coat of plates
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
PATTERN_CHESTPIECE = ['ubody']
PATTERN_TAILGUARD  = ['tail']

PADDED_DOUBLET = ArmorTemplate('Doublet', ARMORTYPE_PADDED, MATERIAL_LINEN, PATTERN_ARMOR)
PADDED_GAMBESON = ArmorTemplate('Gambeson', ARMORTYPE_PADDED, MATERIAL_LINEN, PATTERN_SUIT)

LEATHER_CUIRASS    = ArmorTemplate('Cuirass', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_CUIRASS)
LEATHER_ARMOR      = ArmorTemplate('Armor', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_ARMOR)
LEATHER_ARMOR_SUIT = ArmorTemplate('Armor Suit', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_SUIT)

STEEL_BRIGANDINE_CUIRASS = ArmorTemplate('Brigandine Cuirass', ARMORTYPE_SCALED, MATERIAL_STEEL, PATTERN_CUIRASS)
STEEL_BRIGANDINE_HAUBERK = ArmorTemplate('Brigandine Hauberk', ARMORTYPE_SCALED, MATERIAL_STEEL, PATTERN_HAUBERK)

STEEL_MAIL_SHIRT   = ArmorTemplate('Mail Shirt', ARMORTYPE_MAIL, MATERIAL_STEEL, PATTERN_CUIRASS)
STEEL_MAIL_HAUBERK = ArmorTemplate('Mail Hauberk', ARMORTYPE_MAIL, MATERIAL_STEEL, PATTERN_HAUBERK)
STEEL_MAIL_SUIT    = ArmorTemplate('Mail Suit', ARMORTYPE_MAIL, MATERIAL_STEEL, PATTERN_SUIT)

STEEL_BANDED_MAIL_CUIRASS = ArmorTemplate('Banded Plate Cuirass', ARMORTYPE_BANDED, MATERIAL_STEEL, PATTERN_CUIRASS)
STEEL_BANDED_MAIL_ARMOR   = ArmorTemplate('Banded Plate Armor (Half-Suit)', ARMORTYPE_BANDED, MATERIAL_STEEL, PATTERN_ARMOR)

STEEL_HALF_PLATE_CUIRASS = ArmorTemplate('Half-Plate Cuirass', ARMORTYPE_HALF_PLATE, MATERIAL_STEEL, PATTERN_CUIRASS)
STEEL_HALF_PLATE_ARMOR   = ArmorTemplate('Half-Plate Armor (Half-Suit)', ARMORTYPE_HALF_PLATE, MATERIAL_STEEL, PATTERN_ARMOR)

STEEL_PLATE_MAIL_CUIRASS = ArmorTemplate('Splinted Plate Cuirass', ARMORTYPE_SPLINTED, MATERIAL_STEEL, PATTERN_CUIRASS)
STEEL_PLATE_MAIL_ARMOR   = ArmorTemplate('Splinted Plate Armor (Half-Suit)', ARMORTYPE_SPLINTED, MATERIAL_STEEL, PATTERN_ARMOR)
STEEL_PLATE_MAIL_SUIT    = ArmorTemplate('Splinted Plate Armor', ARMORTYPE_SPLINTED, MATERIAL_STEEL, PATTERN_SUIT)

STEEL_FULL_PLATE_CUIRASS = ArmorTemplate('Full-Plate Cuirass', ARMORTYPE_FULL_PLATE, MATERIAL_STEEL, PATTERN_CUIRASS)
STEEL_FULL_PLATE_ARMOR   = ArmorTemplate('Full-Plate Armor (Half-Suit)', ARMORTYPE_FULL_PLATE, MATERIAL_STEEL, PATTERN_ARMOR)
STEEL_FULL_PLATE_SUIT    = ArmorTemplate('Full-Plate Armor', ARMORTYPE_FULL_PLATE, MATERIAL_STEEL, PATTERN_SUIT)

LEATHER_CAP    = ArmorTemplate('Cap', ARMORTYPE_PADDED, MATERIAL_LEATHER, PATTERN_HELMET)
LEATHER_HELMET = ArmorTemplate('Helmet', ARMORTYPE_LAMINATED, MATERIAL_LEATHER, PATTERN_HELMET)

STEEL_HELMET    = ArmorTemplate('Kettle Helmet', ARMORTYPE_SCALED, MATERIAL_STEEL, PATTERN_HELMET)
STEEL_GREATHELM = ArmorTemplate('Great Helmet', ARMORTYPE_MAIL, MATERIAL_STEEL, PATTERN_HELMET)

STEEL_MORION    = ArmorTemplate('Morion Helmet', ARMORTYPE_SCALED, MATERIAL_STEEL, PATTERN_HELMET)
STEEL_CLOSEHELM = ArmorTemplate('Close Helmet', ARMORTYPE_SPLINTED, MATERIAL_STEEL, PATTERN_HELMET)
STEEL_ARMET     = ArmorTemplate('Armet', ARMORTYPE_FULL_PLATE, MATERIAL_STEEL, PATTERN_HELMET)



