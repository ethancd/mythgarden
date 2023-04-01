NORTH = 'NORTH'
EAST = 'EAST'
SOUTH = 'SOUTH'
WEST = 'WEST'

DIRECTIONS = [
    (NORTH, 'North'),
    (EAST, 'East'),
    (SOUTH, 'South'),
    (WEST, 'West'),
]

MAX_ITEMS = 6

MINUTES_IN_A_DAY = 24 * 60
MINUTES_IN_A_HALF_DAY = 12 * 60
MINUTES_IN_A_QUARTER_DAY = 6 * 60
DAWN = MINUTES_IN_A_QUARTER_DAY
OVERSLEPT_TIME = 10 * 60
SUNSET = 18 * 60

SUNDAY = 'SUN'
MONDAY = 'MON'
TUESDAY = 'TUE'
WEDNESDAY = 'WED'
THURSDAY = 'THU'
FRIDAY = 'FRI'
SATURDAY = 'SAT'

DAYS_OF_WEEK = [
    (MONDAY, 'Mon'),
    (TUESDAY, 'Tue'),
    (WEDNESDAY, 'Wed'),
    (THURSDAY, 'Thu'),
    (FRIDAY, 'Fri'),
    (SATURDAY, 'Sat'),
    (SUNDAY, 'Sun'),
]

FIRST_DAY = DAYS_OF_WEEK[0][0]

DAY_TO_INDEX = {
    MONDAY: 0,
    TUESDAY: 1,
    WEDNESDAY: 2,
    THURSDAY: 3,
    FRIDAY: 4,
    SATURDAY: 5,
    SUNDAY: 6,
}

KOIN_SIGN = '⚜️'

SEED = 'SEED'
SPROUT = 'SPROUT'
CROP = 'CROP'
GIFT = 'GIFT'
FISH = 'FISH'
MINERAL = 'MINERAL'
FOSSIL = 'FOSSIL'
TECH = 'TECH'
MAGIC = 'MAGIC'
HERB = 'HERB'
FLOWER = 'FLOWER'
BERRY = 'BERRY'

ITEM_EMOJIS = {
    SEED: '🌰',
    SPROUT: '🌱',
    CROP: '🌾',
    GIFT: '🎁',
    FISH: '🐟',
    MINERAL: '💎',
    FOSSIL: '🦴',
    TECH: '⚙️',
    MAGIC: '✨',
    HERB: '🌿',
    FLOWER: '🌸',
    BERRY: '🍓',
}

ITEM_TYPES = [
    (SEED, 'Seed'),
    (SPROUT, 'Sprout'),
    (CROP, 'Crop'),
    (GIFT, 'Gift'),
    (FISH, 'Fish'),
    (MINERAL, 'Mineral'),
    (FOSSIL, 'Fossil'),
    (TECH, 'Tech'),
    (MAGIC, 'Magic'),
    (HERB, 'Herb'),
    (FLOWER, 'Flower'),
    (BERRY, 'Berry'),
]

COMMON = 'COMMON'
UNCOMMON = 'UNCOMMON'
RARE = 'RARE'
EPIC = 'EPIC'

RARITIES = [
    COMMON,
    UNCOMMON,
    RARE,
    EPIC
]

RARITY_CHOICES = [
    (COMMON, 'common'),
    (UNCOMMON, 'uncommon'),
    (RARE, 'rare'),
    (EPIC, 'epic'),
]

RARITY_WEIGHTS = {
    COMMON: 0.65,
    UNCOMMON: 0.2,
    RARE: 0.1,
    EPIC: 0.05,
}

CROP_PROFIT_MULTIPLIER = 10

LOVE = 'LOVE'
LIKE = 'LIKE'
NEUTRAL = 'NEUTRAL'
DISLIKE = 'DISLIKE'
HATE = 'HATE'

VALENCES = [
    (LOVE, 'love'),
    (LIKE, 'like'),
    (NEUTRAL, 'neutral'),
    (DISLIKE, 'dislike'),
    (HATE, 'hate'),
]

MINOR = 'MINOR'
MEDIUM = 'MEDIUM'
MAJOR = 'MAJOR'
GRAND = 'GRAND'
SUPREME = 'SUPREME'

MERCH_SLOT_TYPES = [
    (MINOR, 'minor'),
    (MEDIUM, 'medium'),
    (MAJOR, 'major'),
    (GRAND, 'grand'),
    (SUPREME, 'supreme'),
]

BASIC_MERCH_TYPE_TO_RARITY_MAPPING = {
    MINOR: COMMON,
    MEDIUM: UNCOMMON,
    MAJOR: RARE,
    GRAND: EPIC,
    SUPREME: None
}

PREMIUM_MERCH_TYPE_TO_RARITY_MAPPING = {
    MINOR: None,
    MEDIUM: COMMON,
    MAJOR: UNCOMMON,
    GRAND: RARE,
    SUPREME: EPIC
}

BASIC_ITEM_TYPES = [
    FISH,
    FOSSIL,
    HERB,
    BERRY,
]

PREMIUM_ITEM_TYPES = [
    FLOWER,
    MINERAL,
    TECH,
    MAGIC
]

FARM = 'FARM'
TOWN = 'TOWN'
MOUNTAIN = 'MOUNTAIN'
FOREST = 'FOREST'
BEACH = 'BEACH'
SHOP = 'SHOP'
HOME = 'HOME'

WILD_TYPES = ['MOUNTAIN', 'FOREST', 'BEACH']

PLACE_TYPES = [
    (FARM, 'Farm'),
    (MOUNTAIN, 'Mountain'),
    (FOREST, 'Forest'),
    (BEACH, 'Beach'),
    (TOWN, 'Town'),
    (SHOP, 'Shop'),
    (HOME, 'Home'),
]

IMAGE_PREFIX = 'mythgarden/images'

PLACE_IMAGE_DIR = 'places'
FARMER_PORTRAIT_DIR = 'portraits/farmer'
VILLAGER_PORTRAIT_DIR = 'portraits/villager'

DEFAULT_PORTRAIT = 'default.png'

FISHING_DESCRIPTION = 'Go fishing'
DIGGING_DESCRIPTION = 'Dig for something interesting'
FORAGING_DESCRIPTION = 'Forage for plants'
EXIT_DESCRIPTION = 'Exit'

WELCOME_MESSAGE = 'Welcome to Mythgarden! You have one week to grow crops, make friends, and find treasures. Ooh and you can pick an avatar and change your name if you want! Good luck and have fun!'

TALK_MINUTES_PER_FRIENDLINESS = 10

BOOST_DENOMINATOR = 30  # means that every level of boost reduces action time by 1/30th, aka from 90->87, 60->58, 30->29, 5->4
MAX_BOOST_LEVEL = BOOST_DENOMINATOR - 5  # max boost will reduce all action times by 25/30ths, aka from 90->15, 60->10, 30->5, 5->0

KYS_MESSAGE = 'Whether out of despair, boredom, tactical necessity, or a whimsical fit of pique, you hurl yourself off a nearby cliff to your death. A few moments later, you brush the dirt off your dauntless shoulders and enter the time loop to begin the week again.'
