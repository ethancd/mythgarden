from .models import Bridge, Action, Item


def gen_available_actions(situation):
    """Returns a list of available actions for the hero in the current situation, taking into account:
    - the location's landmarks and bridges
    - the situations current contents and occupants
    - the hero's current inventory"""

    actions = []

    place = situation.place
    landmarks = place.landmarks.all()
    inventory = situation.hero.rucksack.contents.all()

    if landmarks.filter(landmark_type=0).exists():  # field
        actions += gen_farming_actions(situation.contents, inventory)

    if landmarks.filter(landmark_type=1).exists():  # shop
        actions += gen_shopping_actions(situation.contents, inventory)

    bridges = Bridge.objects.filter(place_1=place) | Bridge.objects.filter(place_2=place)

    if bridges.exists():
        actions += gen_travel_actions(place, bridges)

    if situation.occupants.exists():
        actions += gen_social_actions(situation.occupants, inventory)

    return actions


def gen_farming_actions(contents, inventory):
    """Returns a list of farming actions: what seeds can be planted from the inventory,
    and what crops can be watered or harvested from the contents (of the field)"""

    actions = []

    seeds = inventory.filter(item_type=Item.SEED)

    for seed in seeds:
        actions.append(Action.create(
            description=f'Plant {seed.name}',
            action_type=Action.PLA,
            target_object=seed,
            cost_amount=30,
            cost_unit=Action.MIN,
            log_statement=f'You planted some {seed.name} in the field.',
        ))

    shoots = contents.filter(item_type=Item.SHOOT)

    for shoot in shoots:
        actions.append(Action.create(
            description=f'Water {shoot.name}',
            action_type=Action.WAT,
            target_object=shoot,
            cost_amount=1,
            cost_unit=Action.HOUR,
            log_statement=f'You watered the {shoot.name} shoots.',
        ))

    crops = contents.filter(item_type=Item.CROP)

    for crop in crops:
        actions.append(Action.create(
            description=f'Harvest {crop.name}',
            action_type=Action.HAR,
            target_object=crop,
            cost_amount=1,
            cost_unit=Action.HOUR,
            log_statement=f'You harvested the {crop.name} crop.',
        ))

    return actions


def gen_shopping_actions(contents, inventory):
    """Returns a list of shopping actions: what items can be sold from inventory,
    and what items can be bought from the contents (of the shop)"""

    actions = []

    for item in contents:
        actions.append(Action.create(
            description=f'Buy {item.name}',
            action_type=Action.BUY,
            target_object=item,
            cost_amount=item.price,
            cost_unit=Action.KOIN,
            log_statement=f'You bought a {item.name} for {item.price}.',
        ))

    for item in inventory:
        actions.append(Action.create(
            description=f'Sell {item.name}',
            action_type=Action.SEL,
            target_object=item,
            cost_amount=-item.price,
            cost_unit=Action.KOIN,
            log_statement=f'You sold a {item.name} for {item.price}.',
        ))

    return actions


def gen_travel_actions(place, bridges):
    """Returns a list of travel actions: what directions you can walk to cross a bridge another place"""

    actions = []

    for bridge in bridges:
        if bridge.place_1 == place:
            destination = bridge.place_2
            direction = bridge.place_2_relative_direction()
        else:
            destination = bridge.place_1
            direction = bridge.place_1_relative_direction()

        actions.append(Action.create(
            description=f'Walk {direction.get_direction_display()}',
            action_type=Action.TRA,
            target_object=destination,
            travel_direction=direction,
            cost_amount=1,
            cost_unit=Action.HOUR,
            log_statement=f'You travelled {direction.get_direction_display()} to {destination.name}.',
        ))

    return actions


def gen_social_actions(villagers, inventory):
    """Returns a list of social actions: which villagers can be talked to,
    and what items can be given to them as gifts"""

    actions = []

    gift_items = inventory.filter(item_type=Item.GIFT)

    for villager in villagers:
        actions.append(Action.create(
            description=f'Talk to {villager.name}',
            action_type=Action.TAL,
            target_object=villager,
            cost_amount=1,
            cost_unit=Action.HOUR,
            log_statement=f'You talked to {villager.name}.',
        ))

        for item in gift_items:
            actions.append(Action.create(
                description=f'Give {item.name} to {villager.name}',
                action_type=Action.GIV,
                target_object=item,
                secondary_target_object=villager,
                cost_amount=15,
                cost_unit=Action.MIN,
                log_statement=f'You gave a {item.name} to {villager.name}.',
            ))

    return actions
