import random

from .models import Bridge, Action, Item, Villager, Place, Building, Session, VillagerState, ItemTypePreference

from .static_helpers import guard_type, guard_types


def can_afford_action(wallet, requested_action):
    if requested_action.is_cost_in_money() and requested_action.action_type != Action.SEL:
        return wallet.money >= requested_action.cost_amount
    else:
        return True


class ActionGenerator:
    def gen_available_actions(self, place, inventory, contents, villagers):
        """Returns a list of available actions for the hero in the current session, taking into account:
        - the current inventory
        - the location's current present items/occupants (contents and villagers)
        - the place's static features (buildings and bridges)"""

        print(f'gen_available_actions: place={place}, inventory={inventory}, contents={contents}, villagers={villagers}')
        available_actions = []

        buildings = list(place.buildings.all())
        bridges = list(Bridge.objects.filter(place_1=place) | Bridge.objects.filter(place_2=place))

        if place.place_type == Place.FARM:
            available_actions += self.gen_farming_actions(contents, inventory)

        if place.place_type == Place.SHOP:
            available_actions += self.gen_shopping_actions(contents, inventory)

        if place.place_type in Place.WILD_TYPES:
            available_actions += self.gen_gather_actions(place)

        if len(buildings) > 0:
            available_actions += self.gen_enter_actions(buildings)

        try:
            building = place.building
            if building.surround is not None:
                available_actions += [self.gen_exit_action(building, building.surround)]
        except Building.DoesNotExist:
            pass

        if len(bridges) > 0:
            available_actions += self.gen_travel_actions(place, bridges)

        if len(villagers) > 0:
            available_actions += self.gen_social_actions(villagers, inventory)

        return available_actions

    def gen_farming_actions(self, field_contents, inventory):
        """Returns a list of farming actions: what seeds can be planted from the inventory,
        and what crops can be watered or harvested from the field contents"""

        guard_types(field_contents, Item)
        guard_types(inventory, Item)

        actions = []

        seeds = [i for i in inventory if i.item_type == Item.SEED]
        for seed in seeds:
            actions.append(self.gen_plant_action(seed))

        sprouts = [i for i in field_contents if i.item_type == Item.SPROUT]
        for sprout in sprouts:
            actions.append(self.gen_water_action(sprout))

        crops = [i for i in field_contents if i.item_type == Item.CROP]

        for crop in crops:
            actions.append(self.gen_harvest_action(crop))

        return actions

    def gen_shopping_actions(self, shop_contents, inventory):
        """Returns a list of shopping actions: what items can be sold from inventory,
        and what items can be bought from the shop contents"""
        guard_types(shop_contents, Item)
        guard_types(inventory, Item)

        actions = []

        for item in shop_contents:
            actions.append(self.gen_buy_action(item))

        for item in inventory:
            actions.append(self.gen_sell_action(item))

        return actions

    def gen_gather_actions(self, place):
        """Returns a list of gathering actions tied to the current place type"""
        guard_type(place, Place)

        actions = []

        if place.place_type == Place.FOREST:
            actions.append(self.gen_foraging_action())
        elif place.place_type == Place.MOUNTAIN:
            actions.append(self.gen_digging_action())
        elif place.place_type == Place.BEACH:
            actions.append(self.gen_fishing_action())

        return actions

    def gen_enter_actions(self, buildings):
        """Returns a list of enter actions: what buildings can be entered"""
        guard_types(buildings, Building)

        actions = []

        for building in buildings:
            actions.append(self.gen_enter_action(building))

        return actions

    def gen_travel_actions(self, place, bridges):
        """Returns a list of travel actions: what directions you can walk to cross a bridge another place"""
        guard_type(place, Place)
        guard_types(bridges, Bridge)

        actions = []

        for bridge in bridges:
            if bridge.place_1 == place:
                destination = bridge.place_2
                direction = bridge.direction_2
                display_direction = bridge.get_direction_2_display()
            else:
                destination = bridge.place_1
                direction = bridge.direction_1
                display_direction = bridge.get_direction_1_display()

            actions.append(self.gen_travel_action(destination, direction, display_direction))

        return actions

    def gen_social_actions(self, villagers, inventory):
        """Returns a list of social actions: which villagers can be talked to,
        and what items can be given to them as gifts"""
        guard_types(villagers, Villager)
        guard_types(inventory, Item)

        actions = []

        for villager in villagers:
            actions.append(self.gen_talk_action(villager))

            for item in inventory:
                actions.append(self.gen_give_action(item, villager))

        return actions

    def gen_give_action(self, item, villager):
        """Returns an action that gives passed item to passed villager"""
        return Action(
            description=f'Give {item.name} to {villager.name}',
            action_type=Action.GIV,
            target_object=villager,
            secondary_target_object=item,
            cost_amount=5,
            cost_unit=Action.MIN,
            log_statement='You gave {item_name} to {villager_name}. Looks like they {valence_text}',
        )

    def gen_talk_action(self, villager):
        """Returns an action that talks to given villager"""

        return Action(
            description=f'Talk to {villager.name}',
            action_type=Action.TAL,
            target_object=villager,
            cost_amount=villager.talk_duration,
            cost_unit=Action.MIN,
            log_statement=f'You talked to {villager.name}.',
        )

    def gen_sell_action(self, item):
        """Returns an action that sells given item"""
        return Action(
            description=f'Sell {item.name}',
            action_type=Action.SEL,
            target_object=item,
            cost_amount=item.price,
            cost_unit=Action.KOIN,
            log_statement=f'You sold {item.name} for {item.price} koin.',
        )

    def gen_buy_action(self, item):
        """Returns an action that buys given item"""
        return Action(
            description=f'Buy {item.name}',
            action_type=Action.BUY,
            target_object=item,
            cost_amount=item.price,
            cost_unit=Action.KOIN,
            log_statement=f'You bought {item.name} for {item.price} koin.',
        )

    def gen_enter_action(self, building):
        """Returns an action that enters given building"""
        return Action(
            description=f'Enter {building.name}',
            action_type=Action.TRA,
            target_object=building,
            cost_amount=5,
            cost_unit=Action.MIN,
            log_statement=f'You entered {building.name}.',
        )

    def gen_exit_action(self, building, surround):
        """Returns an action that exits the current place"""
        return Action(
            description=f'Exit {building.name}',
            action_type=Action.TRA,
            target_object=surround,
            cost_amount=5,
            cost_unit=Action.MIN,
            log_statement=f'You exited {building.name} back out to {surround.name}.',
        )

    def gen_plant_action(self, seed):
        """Returns an action that plants given seed"""
        return Action(
            description=f'Plant {seed.name}',
            action_type=Action.PLA,
            target_object=seed,
            cost_amount=30,
            cost_unit=Action.MIN,
            log_statement=f'You planted some {seed.name} in the field.',
        )

    def gen_water_action(self, sprout):
        """Returns an action that waters given sprout"""
        return Action(
            description=f'Water {sprout.name}',
            action_type=Action.WAT,
            target_object=sprout,
            cost_amount=60,
            cost_unit=Action.MIN,
            log_statement=f'You watered the {sprout.name} sprouts.',
        )

    def gen_harvest_action(self, crop):
        """Returns an action that harvests given crop"""
        return Action(
            description=f'Harvest {crop.name}',
            action_type=Action.HAR,
            target_object=crop,
            cost_amount=60,
            cost_unit=Action.MIN,
            log_statement=f'You harvested the {crop.name} crop.',
        )

    def gen_travel_action(self, destination, direction, display_direction):
        """Returns an action that travels to given destination in given direction"""
        return Action(
            description=f'Walk {display_direction}',
            action_type=Action.TRA,
            target_object=destination,
            direction=direction,
            cost_amount=60,
            cost_unit=Action.MIN,
            log_statement=f'You travelled {display_direction} to {destination.name}.',
        )

    def gen_fishing_action(self):
        """Returns an action that catches a fish"""
        return Action(
            description='Go fishing',
            action_type=Action.GAT,
            cost_amount=60,
            cost_unit=Action.MIN,
            log_statement='You caught a {result}!',
        )

    def gen_digging_action(self):
        """Returns an action that digs for minerals, gems, fossils, etc"""
        return Action(
            description='Dig for something interesting',
            action_type=Action.GAT,
            cost_amount=90,
            cost_unit=Action.MIN,
            log_statement='You dug up a {result}!',
        )

    def gen_foraging_action(self):
        """Returns an action that forages for herbs, plants, etc"""
        return Action(
            description='Forage for plants',
            action_type=Action.GAT,
            cost_amount=30,
            cost_unit=Action.MIN,
            log_statement='You found {result}!',
        )


class ActionExecutor:
    def execute(self, action, session):
        """Executes the given action, modifying relevant models in the session, and returns updated
        (selecting the correct method based on the action type using a bit of meta programming, as a treat)"""
        guard_type(action, Action)
        guard_type(session, Session)

        ex = f'execute_{action.get_action_type_display().lower()}_action'

        if hasattr(self, ex) and callable(getattr(self, ex)):
            return getattr(self, ex)(action, session)
        else:
            raise Exception(f'Unknown action type: {action.get_action_type_display().lower()}')

    def execute_travel_action(self, action, session):
        """Executes a travel action, which updates the hero's current location and ticks the clock"""

        session.location = action.target_object
        session.clock.advance(action.cost_amount)

        session.save_data()

        return ({
                    'place': session.location,
                    'clock': session.clock,
                    'buildings': list(session.location.buildings.all()),
                    'place_contents': list(session.location_state.contents.all()),
                    'villager_states': list(session.occupant_states.all())
                }, action.log_statement)

    def execute_talk_action(self, action, session):
        """Executes a talk action, which displays some dialogue, adds to the villager's affinity, and ticks the clock"""
        # also want to set villager_state to has_been_greeted so we can't talk to them again till tomorrow

        villager = action.target_object
        is_next_tier = self.update_affinity(villager, villager.friendliness, session)
        # dialogue = villager.get_dialogue(session)

        session.clock.advance(action.cost_amount)

        session.save_data()

        log_statement = self.add_affinity_tag_if_needed(action.log_statement, is_next_tier, villager)

        return ({
                    'clock': session.clock,
                    'villager_states': list(session.occupant_states.all()),
                    # 'dialogue': dialogue,
                }, log_statement)

    def execute_give_action(self, action, session):
        """Executes a give action, which removes an item from the hero's inventory
        and adds to the villager's affinity"""
        # also want to set villager_state to has_been_gifted so we can't talk to them again till tomorrow

        villager = action.target_object
        gift = action.secondary_target_object
        valence = villager.gift_valence(gift)
        affinity_amount = self.calc_gift_affinity_change(valence, gift.rarity, villager.friendliness)
        is_next_tier = self.update_affinity(villager, affinity_amount, session)
        # dialogue = villager.get_dialogue(session)

        session.clock.advance(action.cost_amount)
        session.inventory.items.remove(gift)

        session.save_data()

        valence_text = self.get_valence_text(valence)
        base_statement = action.log_statement.format(item_name=gift.name, villager_name=villager.name, valence_text=valence_text)

        log_statement = self.add_affinity_tag_if_needed(base_statement, is_next_tier, villager)

        session.save_data()

        return ({
                    'inventory': list(session.inventory.items.all()),
                    'villager_states': list(session.occupant_states.all()),
                    # 'dialogue': dialogue,
                }, log_statement)

    def execute_sell_action(self, action, session):
        """Executes a sell action, which moves an item from the hero's inventory into the session contents
        and adds the price in koin to the hero's wallet"""

        session.inventory.items.remove(action.target_object)
        session.location_state.contents.add(action.target_object)
        session.wallet.money += action.cost_amount

        session.save_data()

        return ({
                    'wallet': session.wallet,
                    'inventory': list(session.inventory.items.all()),
                    'place_contents': list(session.location_state.contents.all()),
                }, action.log_statement)

    def execute_buy_action(self, action, session):
        """Executes a buy action, which moves an item from the session contents into the hero's inventory
        and deducts the price in koin from the hero's wallet"""

        session.inventory.items.add(action.target_object)
        session.location_state.contents.remove(action.target_object)
        session.wallet.money -= action.cost_amount

        session.save_data()

        return ({
                    'wallet': session.wallet,
                    'inventory': list(session.inventory.items.all()),
                    'place_contents': list(session.location_state.contents.all()),
                }, action.log_statement)

    def execute_plant_action(self, action, session):
        """Executes a plant action, which moves a seed from the hero's inventory into the session contents"""

        session.inventory.items.remove(action.target_object)
        session.location_state.contents.add(action.target_object)

        session.save_data()

        return ({
                    'inventory': list(session.inventory.items.all()),
                    'place_contents': list(session.location_state.contents.all()),
                }, action.log_statement)

    def execute_water_action(self, action, session):
        raise NotImplementedError()

    def execute_harvest_action(self, action, session):
        """Executes a harvest action, which moves a crop from the session contents into the hero's inventory"""

        session.inventory.items.add(action.target_object)
        session.location_state.contents.remove(action.target_object)

        session.save_data()

        return ({
                    'inventory': list(session.inventory.items.all()),
                    'place_contents': list(session.location_state.contents.all()),
                }, action.log_statement)

    def execute_gather_action(self, action, session):
        """Executes a gather action, which finds a random item in the current location's item pool
        and adds a copy to the hero's inventory"""

        item = self.pull_item_from_pool(session.location)
        session.inventory.items.add(item)
        session.clock.advance(action.cost_amount)

        session.save_data()

        log_statement = action.log_statement.format(result=item.name)

        return ({
                    'inventory': list(session.inventory.items.all()),
                    'clock': session.clock,
                }, log_statement)

    def calc_gift_affinity_change(self, valence, rarity, friendliness):
        """Calculates the change in affinity for a gift based on valence of villager's reaction,
        item's rarity, villager's friendliness"""

        VALENCE_VALUE_MAP = {
            ItemTypePreference.LOVE: 20,
            ItemTypePreference.LIKE: 6,
            ItemTypePreference.NEUTRAL: 2,
            ItemTypePreference.DISLIKE: 0,
            ItemTypePreference.HATE: -2,
        }

        RARITY_MULTIPLIER_MAP = {
            Item.COMMON: 0.5,
            Item.UNCOMMON: 1,
            Item.RARE: 2,
            Item.EPIC: 4,
        }

        base_value = VALENCE_VALUE_MAP[valence]
        multiplier = RARITY_MULTIPLIER_MAP[rarity]

        return int((base_value * multiplier) + friendliness)

    def update_affinity(self, villager, amount, session):
        """Updates the villager's villager_state affinity
        and returns whether the villager is in a new affinity tier"""

        villager_state = session.occupant_states.filter(villager=villager).first()

        old_affinity = villager_state.affinity
        new_affinity = villager_state.add_affinity(amount)

        print(f'Villager has gone from {old_affinity} hearts to {new_affinity} hearts')

        return self.is_next_affinity_tier(old_affinity, new_affinity)

    def is_next_affinity_tier(self, old_affinity, new_affinity, tier_size=VillagerState.AFFINITY_TIER_SIZE):
        # e.g. tier size 20, old_affinity 35, new_affinity 45
        # villager just crossed 40 so is now in new tier
        old_tier = old_affinity // tier_size
        new_tier = new_affinity // tier_size

        return old_tier != new_tier

    def add_affinity_tag_if_needed(self, base_statement, is_next_tier, villager):
        if is_next_tier:
            return base_statement + f' You and {villager.name} have developed more of a bond! +❤️'
        else:
            return base_statement

    def get_valence_text(self, valence):
        if valence == ItemTypePreference.LOVE:
            return 'love it!'
        elif valence == ItemTypePreference.LIKE:
            return 'like it!'
        elif valence == ItemTypePreference.NEUTRAL:
            return 'feel okay about it.'
        elif valence == ItemTypePreference.DISLIKE:
            return 'aren\'t a fan of it.'
        elif valence == ItemTypePreference.HATE:
            return 'wish you hadn\'t!'
        else:
            raise ValueError(f'Invalid valence {valence}')

    def pull_item_from_pool(self, location):
        """Returns a random item from the given location's item pool, weighted by rarity"""

        # Pick a rarity, find an item of that rarity;
        # if none found, try again with another rarity;
        # if no items at all, error out
        rarities = [r for r in Item.RARITIES]
        while len(rarities) > 0:
            weights = [Item.RARITY_WEIGHTS[r] for r in rarities]
            rarity = random.choices(rarities, weights=weights, k=1)[0]
            choices = location.item_pool.filter(rarity=rarity)

            if choices.count() > 0:
                item = choices.order_by('?').first()
                return item
            else:
                print(f'No items found in {location.name} of rarity {rarity}, trying other rarities...')
                rarities.remove(rarity)
                continue

        raise ValueError(f'No items found in location {location.name} of any rarity')
