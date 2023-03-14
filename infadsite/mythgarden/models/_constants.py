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
    (SUNDAY, 'Sun'),
    (MONDAY, 'Mon'),
    (TUESDAY, 'Tue'),
    (WEDNESDAY, 'Wed'),
    (THURSDAY, 'Thu'),
    (FRIDAY, 'Fri'),
    (SATURDAY, 'Sat'),
]

DAY_TO_INDEX = {
    SUNDAY: 0,
    MONDAY: 1,
    TUESDAY: 2,
    WEDNESDAY: 3,
    THURSDAY: 4,
    FRIDAY: 5,
    SATURDAY: 6,
}

KOIN_SIGN = '⚜️'

SEED = 'SEED'
SPROUT = 'SPROUT'
CROP = 'CROP'
GIFT = 'GIFT'
FISH = 'FISH'
MINERAL = 'MINERAL'
ARTIFACT = 'ARTIFACT'
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
    ARTIFACT: '🗿',
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
    (ARTIFACT, 'Artifact'),
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

IMAGE_PREFIX = 'mythgarden/images/'

FISHING_DESCRIPTION = 'Go fishing'
DIGGING_DESCRIPTION = 'Dig for something interesting'
FORAGING_DESCRIPTION = 'Forage for plants'

WELCOME_MESSAGE = 'Welcome to Mythgarden! You have one week to grow crops, make friends, and find treasures. Good luck and have fun!'

TALK_MINUTES_PER_FRIENDLINESS = 10