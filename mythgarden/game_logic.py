import random
import math
import json

from .models import Bridge, Action, Place, Building, Session, VillagerState, Item, ItemToken, \
    DialogueLine, ScheduledEvent, ScheduledEventState, PlaceState, MerchSlot
from .models._constants import SEED, SPROUT, CROP, COMMON, UNCOMMON, RARE, EPIC, RARITIES, RARITY_WEIGHTS, FARM, SHOP, \
    WILD_TYPES, FOREST, MOUNTAIN, BEACH, LOVE, LIKE, NEUTRAL, DISLIKE, HATE, FIRST_DAY, DAWN, FISHING_DESCRIPTION, \
    DIGGING_DESCRIPTION, FORAGING_DESCRIPTION, SUNSET, TALK_MINUTES_PER_FRIENDLINESS, MAX_BOOST_LEVEL, \
    BOOST_DENOMINATOR, KYS_MESSAGE, EXIT_DESCRIPTION, DAYS_OF_WEEK, MAX_ITEMS
from .static_helpers import guard_type, guard_types


def can_afford_action(wallet, requested_action):
    if requested_action.is_cost_in_money() and requested_action.action_type != Action.SELL:
        return wallet.money >= requested_action.cost_amount
    else:
        return True


class ActionGenerator:
    def get_actions_for_session(self, session):
        place = session.location
        inventory = list(session.inventory.item_tokens.all())
        contents = list(session.local_item_tokens.all())
        villager_states = list(session.occupant_states.all())
        clock = session.clock
        boost_level = session.hero.boost_level

        actions = self.gen_available_actions(place, inventory, contents, villager_states, clock, boost_level)

        return actions

    def gen_available_actions(self, place, inventory, contents, villager_states, clock, boost_level):
        """Returns a list of available actions for the hero in the current session, taking into account:
        - the current inventory
        - the location's current present items/occupants (contents and villagers)
        - the place's static features (buildings and bridges)"""

        available_actions = []

        buildings = list(place.buildings.all())
        bridges = list(Bridge.objects.filter(place_1=place) | Bridge.objects.filter(place_2=place))

        try:
            building = place.building
            if building.surround is not None:
                available_actions += [self.gen_exit_action(building)]
        except Building.DoesNotExist:
            pass

        if len(bridges) > 0:
            available_actions += self.gen_travel_actions(place, bridges)

        if len(buildings) > 0:
            available_actions += self.gen_enter_actions(buildings)

        if place.place_type == FARM:
            available_actions += self.gen_farming_actions(contents, inventory)

        if place.place_type == SHOP:
            available_actions += self.gen_shopping_actions(contents, inventory)

        if place.place_type in WILD_TYPES:
            available_actions += self.gen_gather_actions(place)

        if len(villager_states) > 0:
            available_actions += self.gen_social_actions(villager_states, inventory)

        if place.is_farmhouse:
            available_actions += self.gen_storage_actions(contents, inventory)

            if clock.time >= SUNSET:
                available_actions += [self.gen_sleep_action()]

        actions = self.apply_speed_boost(available_actions, boost_level)

        return actions

    def gen_farming_actions(self, field_contents, inventory):
        """Returns a list of farming actions: what seeds can be planted from the inventory,
        and what crops can be watered or harvested from the field contents"""

        guard_types(field_contents, ItemToken)
        guard_types(inventory, ItemToken)

        actions = []

        seeds = [i for i in inventory if i.item_type == SEED]
        for seed in seeds:
            actions.append(self.gen_plant_action(seed))

        growing_plants = [i for i in field_contents if i.item_type in [SEED, SPROUT]]
        for plant in growing_plants:
            if not plant.has_been_watered:
                actions.append(self.gen_water_action(plant))

        crops = [i for i in field_contents if i.item_type == CROP]

        for crop in crops:
            actions.append(self.gen_harvest_action(crop))

        return actions

    def gen_shopping_actions(self, shop_contents, inventory):
        """Returns a list of shopping actions: what items can be sold from inventory,
        and what items can be bought from the shop contents"""
        guard_types(shop_contents, ItemToken)
        guard_types(inventory, ItemToken)

        actions = []

        for item_token in shop_contents:
            actions.append(self.gen_buy_action(item_token))

        for item_token in inventory:
            actions.append(self.gen_sell_action(item_token))

        return actions

    def gen_gather_actions(self, place):
        """Returns a list of gathering actions tied to the current place type"""
        guard_type(place, Place)

        actions = []

        if place.place_type == FOREST:
            actions.append(self.gen_foraging_action())
        elif place.place_type == MOUNTAIN:
            actions.append(self.gen_digging_action())
        elif place.place_type == BEACH:
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

    def gen_social_actions(self, villager_states, inventory):
        """Returns a list of social actions: which villagers can be talked to,
        and what items can be given to them as gifts"""
        guard_types(villager_states, VillagerState)
        guard_types(inventory, ItemToken)

        talk_actions = []
        gift_actions = []

        for villager_state in villager_states:
            villager = villager_state.villager
            if not villager_state.has_been_talked_to:
                talk_actions.append(self.gen_talk_action(villager))

            if not villager_state.has_been_given_gift:
                for item_token in inventory:
                    gift_actions.append(self.gen_give_action(item_token, villager))

        return talk_actions + gift_actions

    def gen_storage_actions(self, storage_contents, inventory):
        """Returns a list of storage actions: what items can be moved from inventory to storage,
        and what items can be taken from the storage into inventory"""
        guard_types(storage_contents, ItemToken)
        guard_types(inventory, ItemToken)

        actions = []

        for item_token in inventory:
            actions.append(self.gen_stow_action(item_token))

        for item_token in storage_contents:
            actions.append(self.gen_retrieve_action(item_token))

        return actions

    def gen_give_action(self, item_token, villager):
        """Returns an action that gives passed item to passed villager"""
        cost_amount = 5
        return Action(
            description=f'Gift {item_token.name} to {villager.name}',
            action_type=Action.GIVE,
            target_villager=villager,
            target_item=item_token,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement='You gave {item_name} to {villager_name}. Looks like they {valence_text}',
        )

    def gen_talk_action(self, villager):
        """Returns an action that talks to given villager"""
        cost_amount = villager.friendliness * TALK_MINUTES_PER_FRIENDLINESS
        return Action(
            description=f'Talk to {villager.name}',
            action_type=Action.TALK,
            target_villager=villager,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement=f'You talked to {villager.name}.',
        )

    def gen_sell_action(self, item_token):
        """Returns an action that sells given item"""
        return Action(
            description=f'Sell {item_token.name}',
            action_type=Action.SELL,
            target_item=item_token,
            cost_amount=item_token.price,
            cost_unit=Action.KOIN,
            log_statement=f'You sold {item_token.name} for {item_token.price} koin.',
        )

    def gen_buy_action(self, item_token):
        """Returns an action that buys given item"""
        return Action(
            description=f'Buy {item_token.name}',
            action_type=Action.BUY,
            target_item=item_token,
            cost_amount=item_token.price,
            cost_unit=Action.KOIN,
            log_statement=f'You bought {item_token.name} for {item_token.price} koin.',
        )

    def gen_stow_action(self, item_token):
        """Returns an action that puts given item into storage"""
        return Action(
            description=f'Stow {item_token.name}',
            action_type=Action.STOW,
            target_item=item_token,
            log_statement=f'You put {item_token.name} in your chest.',
        )

    def gen_retrieve_action(self, item_token):
        """Returns an action that takes given item out of storage"""
        return Action(
            description=f'Retrieve {item_token.name}',
            action_type=Action.RETRIEVE,
            target_item=item_token,
            log_statement=f'You took {item_token.name} out of your chest.',
        )

    def gen_enter_action(self, building):
        """Returns an action that enters given building"""
        cost_amount = 5
        return Action(
            description=f'Enter {building.name}',
            action_type=Action.TRAVEL,
            target_place=building,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement=f'You entered {building.name}.',
        )

    def gen_exit_action(self, building):
        """Returns an action that exits the current place"""
        cost_amount = 5
        return Action(
            description=EXIT_DESCRIPTION,
            action_type=Action.TRAVEL,
            target_place=building.surround,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement=f'You exited {building.name}.',
        )

    def gen_plant_action(self, seed_token):
        """Returns an action that plants given seed"""
        cost_amount = 30
        return Action(
            description=f'Plant {seed_token.name}',
            action_type=Action.PLANT,
            target_item=seed_token,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement=f'You planted some {seed_token.name} in the field.',
        )

    def gen_water_action(self, plant_token):
        """Returns an action that waters given seed/sprout"""
        cost_amount = 30
        return Action(
            description=f'Water {plant_token.name}',
            action_type=Action.WATER,
            target_item=plant_token,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement=f'You watered the {plant_token.name}.',
        )

    def gen_harvest_action(self, crop_token):
        """Returns an action that harvests given crop"""
        cost_amount = 30
        return Action(
            description=f'Harvest {crop_token.name}',
            action_type=Action.HARVEST,
            target_item=crop_token,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement=f'You harvested the {crop_token.name}.',
        )

    def gen_travel_action(self, destination, direction, display_direction):
        """Returns an action that travels to given destination in given direction"""
        cost_amount = 60
        return Action(
            description=f'Go {display_direction}',
            action_type=Action.TRAVEL,
            target_place=destination,
            direction=direction,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement=f'You travelled to {destination.name}.',
        )

    def gen_fishing_action(self):
        """Returns an action that catches a fish"""
        cost_amount = 60
        return Action(
            description=FISHING_DESCRIPTION,
            action_type=Action.GATHER,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement='You caught a {result}!',
        )

    def gen_digging_action(self):
        """Returns an action that digs for minerals, gems, fossils, etc"""
        cost_amount = 90
        return Action(
            description=DIGGING_DESCRIPTION,
            action_type=Action.GATHER,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement='You dug up a {result}!',
        )

    def gen_foraging_action(self):
        """Returns an action that forages for herbs, plants, etc"""
        cost_amount = 30
        return Action(
            description=FORAGING_DESCRIPTION,
            action_type=Action.GATHER,
            cost_amount=cost_amount,
            cost_unit=Action.MIN,
            cost_wait_class=Action.MINUTES_TO_WAIT_CLASS[cost_amount],
            log_statement='You found {result}!',
        )

    def gen_sleep_action(self):
        """Returns an action for the hero to go to sleep till the next day"""
        return Action(
            description='Sleep',
            action_type=Action.SLEEP,
            log_statement='You tuck yourself into bed. Sweet dreams!',
        )

    def apply_speed_boost(self, actions, boost_level):
        """Reduce the cost_amount of time-based actions proportional to the given speed_boost"""
        if not boost_level or boost_level == 0:
            return actions

        boost_fraction = 1 - (min(boost_level, MAX_BOOST_LEVEL) / BOOST_DENOMINATOR)

        for action in actions:
            if not action.is_cost_in_money() and action.action_type is not Action.SLEEP:
                action.cost_amount = math.floor(action.cost_amount * boost_fraction)

        return actions

class ActionExecutor:
    def execute(self, action, session):
        """Executes the given action, modifying relevant models in the session, and returns updated
        (selecting the correct method based on the action type using a bit of meta programming, as a treat)"""
        guard_type(action, Action)
        guard_type(session, Session)

        ex = f'execute_{action.get_action_type_display().lower()}_action'

        if hasattr(self, ex) and callable(getattr(self, ex)):
            updated_models = getattr(self, ex)(action, session)
            updated_models['villagerStates'] = list(session.occupant_states.all())
            updated_models['messages'] = list(session.messages.all())
        else:
            raise ValueError(f'Unknown action type: {action.get_action_type_display().lower()}')

        return updated_models

    def execute_travel_action(self, action, session):
        """Executes a travel action, which updates the current location and ticks the clock"""

        session.location = action.target_place
        session.messages.create(text=action.log_statement)

        session.clock.advance(action.cost_amount)

        session.save()
        session.clock.save()

        return {
            'place': session.location,
            'clock': session.clock,
            'buildings': list(session.location.buildings.all()),
            'localItemTokens': list(session.local_item_tokens.all()),
        }

    def execute_talk_action(self, action, session):
        """Executes a talk action, which displays some dialogue, adds to the villager's affinity, and ticks the clock"""

        villager = action.target_villager
        villager_state = session.get_villager_state(villager)

        dialogue = self.__get_dialogue_for_talk_action(villager_state, villager)
        affinity_amount = self.__calc_talk_affinity_change(villager_state.affinity_tier, villager.friendliness)
        hearts_gained = self.__update_affinity(villager_state, affinity_amount)

        session.hero_state.hearts_earned += hearts_gained
        villager_state.mark_as_talked_to()
        affinity_message = self.__make_affinity_message_if_any(hearts_gained, villager)

        session.messages.create(text=action.log_statement)
        if affinity_message:
            session.messages.create(text=affinity_message)

        session.clock.advance(action.cost_amount)

        villager_state.save()
        session.hero_state.save()
        session.clock.save()

        return {
            'hero': session.hero_state,
            'clock': session.clock,
            'dialogue': dialogue,
        }

    def execute_give_action(self, action, session):
        """Executes a give action, which removes an item from the hero's inventory
        and adds to the villager's affinity"""

        villager = action.target_villager
        gift = action.target_item
        valence = villager.gift_valence(gift)
        affinity_amount = self.__calc_gift_affinity_change(valence, gift.rarity)

        villager_state = session.occupant_states.filter(villager=villager).first()
        villager_state.has_been_given_gift = True
        hearts_gained = self.__update_affinity(villager_state, affinity_amount)

        session.hero_state.hearts_earned += hearts_gained

        trigger = self.__get_gift_dialogue_trigger(valence)
        dialogue = villager.get_dialogue(trigger)

        session.inventory.item_tokens.remove(gift)

        valence_text = self.__get_valence_text(valence)
        log_statement = action.log_statement.format(item_name=gift.name, villager_name=villager.name,
                                                    valence_text=valence_text)

        affinity_message = self.__make_affinity_message_if_any(hearts_gained, villager)

        session.messages.create(text=log_statement)
        if affinity_message:
            session.messages.create(text=affinity_message)

        session.clock.advance(action.cost_amount)

        session.hero_state.save()
        villager_state.save()
        session.clock.save()

        return {
            'hero': session.hero_state,
            'clock': session.clock,
            'inventory': list(session.inventory.item_tokens.all()),
            'dialogue': dialogue,
        }

    def execute_sell_action(self, action, session):
        """Executes a sell action, which removes an item from the hero's inventory
        and adds the price in koin to the hero's wallet"""

        item = action.target_item

        session.inventory.item_tokens.remove(item)

        #  if the item should get repopulated into the store, do that
        if item.bought_from_store and item.item_type != SEED:
            matching_item_in_store = session.local_item_tokens.filter(item=item.item)
            store_has_open_slot = session.local_item_tokens.count() < MAX_ITEMS

            if matching_item_in_store.exists():
                matching_item = matching_item_in_store.first()
                matching_item.quantity += 1
                matching_item.save()
            elif store_has_open_slot:
                item.quantity = 1
                item.save()
                session.location_state.item_tokens.add(item)

        session.wallet.money += action.cost_amount
        if not item.bought_from_store:
            session.hero_state.koin_earned += action.cost_amount
            session.hero_state.save()

        session.messages.create(text=action.log_statement)

        session.wallet.save()

        return {
            'hero': session.hero_state,
            'wallet': session.wallet,
            'localItemTokens': list(session.local_item_tokens.all()),
            'inventory': list(session.inventory.item_tokens.all()),
        }

    def execute_buy_action(self, action, session):
        """Executes a buy action, which adds an item_token to the hero's inventory that's a copy of one in the shop,
        and deducts the price in koin from the hero's wallet"""

        item = action.target_item

        new_item = item.make_copy()
        new_item.bought_from_store = True
        new_item.quantity = None
        new_item.save()
        session.inventory.item_tokens.add(new_item)

        if item.quantity:
            item.quantity -= 1

            if item.quantity == 0:
                session.location_state.item_tokens.remove(item)
            else:
                item.save()

        session.wallet.money -= action.cost_amount

        session.messages.create(text=action.log_statement)
        session.wallet.save()

        return {
            'wallet': session.wallet,
            'inventory': list(session.inventory.item_tokens.all()),
            'localItemTokens': list(session.local_item_tokens.all()),
        }

    def execute_stow_action(self, action, session):
        """Executes a stow action, which removes an item from the hero's inventory
        and adds it into location storage"""

        item = action.target_item

        session.inventory.item_tokens.remove(item)
        session.location_state.item_tokens.add(item)

        session.messages.create(text=action.log_statement)

        return {
            'localItemTokens': list(session.local_item_tokens.all()),
            'inventory': list(session.inventory.item_tokens.all()),
        }

    def execute_retrieve_action(self, action, session):
        """Executes a retrieve action, which adds an item into the hero's inventory
        and removes it from location storage"""

        item = action.target_item

        session.location_state.item_tokens.remove(item)
        session.inventory.item_tokens.add(item)

        session.messages.create(text=action.log_statement)

        return {
            'localItemTokens': list(session.local_item_tokens.all()),
            'inventory': list(session.inventory.item_tokens.all()),
        }

    def execute_plant_action(self, action, session):
        """Executes a plant action, which moves a seed from the hero's inventory into the session contents"""

        session.inventory.item_tokens.remove(action.target_item)
        session.location_state.item_tokens.add(action.target_item)

        session.messages.create(text=action.log_statement)

        session.clock.advance(action.cost_amount)
        session.clock.save()

        return {
            'clock': session.clock,
            'inventory': list(session.inventory.item_tokens.all()),
            'localItemTokens': list(session.local_item_tokens.all()),
        }

    def execute_water_action(self, action, session):
        """Executes a water action, which sets the item_token's has_been_watered attribute to True"""

        item_token = action.target_item
        item_token.has_been_watered = True
        item_token.save()

        session.messages.create(text=action.log_statement)

        session.clock.advance(action.cost_amount)
        session.clock.save()

        return {
            'clock': session.clock,
            'localItemTokens': list(session.local_item_tokens.all()),
        }

    def execute_harvest_action(self, action, session):
        """Executes a harvest action, which moves a crop from the session contents into the hero's inventory"""

        session.inventory.item_tokens.add(action.target_item)
        session.location_state.item_tokens.remove(action.target_item)

        session.messages.create(text=action.log_statement)

        session.clock.advance(action.cost_amount)
        session.clock.save()

        return {
            'clock': session.clock,
            'inventory': list(session.inventory.item_tokens.all()),
            'localItemTokens': list(session.local_item_tokens.all()),
        }

    def execute_gather_action(self, action, session):
        """Executes a gather action, which finds a random item in the current location's item pool
        and adds a copy to the hero's inventory"""

        item = self.__pull_item_from_pool(session.location)
        session.inventory.item_tokens.add(ItemToken.objects.create(session=session, item=item))

        log_statement = action.log_statement.format(result=item.name)
        session.messages.create(text=log_statement)

        session.clock.advance(action.cost_amount)
        session.clock.save()

        return {
            'inventory': list(session.inventory.item_tokens.all()),
            'clock': session.clock,
        }

    def execute_sleep_action(self, action, session):
        """Executes a sleep action, which advances the clock to midnight"""

        session.hero_state.is_in_bed = True
        session.messages.create(text=action.log_statement)

        session.clock.advance(session.clock.minutes_to_midnight)

        session.hero_state.save()
        session.clock.save()

        return {
            'clock': session.clock,
        }

    # private methods
    def __get_dialogue_for_talk_action(self, villager_state, villager):
        if villager_state.has_ever_been_talked_to:
            trigger = DialogueLine.TALKED_TO
            affinity_tier = villager_state.affinity_tier
        else:
            trigger = DialogueLine.FIRST_MEETING
            affinity_tier = None

        return villager.get_dialogue(trigger, affinity_tier)

    def __pull_item_from_pool(self, location):
        """Returns a random item from the given location's item pool, weighted by rarity"""

        # Pick a rarity, find an item of that rarity;
        # if none found, try again with another rarity;
        # if no items at all, error out
        rarities = [r for r in RARITIES]

        while len(rarities) > 0:
            weights = [RARITY_WEIGHTS[r] for r in rarities]
            rarity = random.choices(rarities, weights=weights, k=1)[0]

            items_at_rarity = location.item_pool.filter(rarity=rarity)

            # find the item types among items at this rarity, then pick a random type to filter on
            available_types = list(items_at_rarity.values_list("item_type", flat=True).distinct())

            print(available_types)
            item_type = random.choice(available_types)

            choices = items_at_rarity.filter(item_type=item_type)

            if choices.count() > 0:
                item = choices.order_by('?').first()
                return item
            else:
                # 'No items found in location with that rarity, so we try other rarities.
                rarities.remove(rarity)
                continue

        raise ValueError(f'No items found in location {location.name} of any rarity')

    def __calc_talk_affinity_change(self, affinity_tier, friendliness):
        """Calculates the change in affinity for a talk action based on the affinity tier the villager is already at
        and their base friendliness"""

    #    0aff -> 1x
    #    1aff -> 1.5x
    #    2aff -> 2x
    #    3aff -> 2.5x
    #    4aff+ -> 3x

        base_value = friendliness
        multiplier = 1

        return int(base_value * multiplier)

    def __calc_gift_affinity_change(self, valence, rarity):
        """Calculates the change in affinity for a gift based on valence of villager's reaction,
        item's rarity, villager's friendliness"""

        VALENCE_VALUE_MAP = {
            LOVE: 10,
            LIKE: 5,
            NEUTRAL: 2.5,
            DISLIKE: 0,
            HATE: -2.5,
        }

        RARITY_MULTIPLIER_MAP = {
            COMMON: 1,
            UNCOMMON: 2,
            RARE: 3,
            EPIC: 4,
        }

        base_value = VALENCE_VALUE_MAP[valence]
        multiplier = RARITY_MULTIPLIER_MAP[rarity]

        return int(base_value * multiplier)

    def __update_affinity(self, villager_state, amount):
        """Updates the villager's villager_state affinity and returns the number of "hearts" gained (affinity tier diff)"""

        old_tier = villager_state.affinity_tier
        villager_state.add_affinity(amount)
        new_tier = villager_state.affinity_tier

        return new_tier - old_tier

    def __make_affinity_message_if_any(self, hearts_gained, villager):
        if hearts_gained > 0:
            hearts = ''.join(['❤️' for _ in range(hearts_gained)])
            return f"You and {villager.name} have developed more of a bond! +{hearts}"
        else:
            return None

    def __get_valence_text(self, valence):
        if valence == LOVE:
            return 'love it!'
        elif valence == LIKE:
            return 'like it!'
        elif valence == NEUTRAL:
            return 'feel okay about it.'
        elif valence == DISLIKE:
            return 'aren\'t a fan of it.'
        elif valence == HATE:
            return 'wish you hadn\'t!'
        else:
            raise ValueError(f'Invalid valence {valence}')

    def __get_talk_dialogue_trigger(self, villager_state):
        """Returns a dialogue trigger for a talk action based on whether they've been talked to before or not"""
        if villager_state.has_ever_been_talked_to:
            return DialogueLine.TALKED_TO
        else:
            return DialogueLine.FIRST_MEETING

    def __get_gift_dialogue_trigger(self, valence):
        """Returns a trigger object for a gift action based on the valence of their reaction"""

        VALENCE_TO_DIALOGUE_TRIGGER_MAP = {
            LOVE: DialogueLine.LOVED_GIFT,
            LIKE: DialogueLine.LIKED_GIFT,
            NEUTRAL: DialogueLine.NEUTRAL_GIFT,
            DISLIKE: DialogueLine.DISLIKED_GIFT,
            HATE: DialogueLine.HATED_GIFT,
        }

        return VALENCE_TO_DIALOGUE_TRIGGER_MAP[valence]

class EventOperator:
    def react_to_time_passing(self, clock, session):
        # check for game over and short circuit if so
        if self.__is_game_over(clock):
            session.game_over = True
            session.save()
            return

        # if in the middle of the day, just run scheduled events (from database)
        if not clock.is_new_day:
            self.trigger_scheduled_events_for_so_far_today(clock, session)

        # if start of the day, finish yesterday's events, run hard-coded events, run scheduled events, then sleep
        if clock.is_new_day:
            self.trigger_remaining_events_from_yesterday(clock, session)
            self.reset_for_new_day(session)

            self.trigger_scheduled_events_for_so_far_today(clock, session)

            self.fall_asleep(clock, session)  # this advances the clock! must happen after all other events :D

    def trigger_remaining_events_from_yesterday(self, clock, session):
        # If we're starting a new day, then per force we want to trigger any untriggered events that were set
        # to go off yesterday.
        yesterday_index = (clock.day_index - 1)
        yesterday = DAYS_OF_WEEK[yesterday_index][0]

        events_to_trigger_queue = self.__build_events_to_trigger_queue(yesterday, session.event_states)

        self.trigger_events(list(events_to_trigger_queue), session)

    def trigger_scheduled_events_for_so_far_today(self, clock, session):
        events_to_trigger_sometime_today_queue = self.__build_events_to_trigger_queue(clock.day, session.event_states)

        events_to_trigger_queue = events_to_trigger_sometime_today_queue.filter(event__time__lte=clock.time)

        self.trigger_events(list(events_to_trigger_queue), session)

    def trigger_events(self, event_states, session):
        villager_states = VillagerState.objects.select_related('villager').filter(session=session)
        place_states = PlaceState.objects.select_related('place').filter(session=session)

        villager_results = []

        for event_state in event_states:
            result = self.trigger_event(event_state.event, session, villager_states, place_states)
            if isinstance(result, VillagerState):
                villager_results.append(result)

            event_state.has_occurred = True

        ScheduledEventState.objects.bulk_update(event_states, ['has_occurred'])

        if len(villager_results) > 0:
            VillagerState.objects.bulk_update(villager_results, ['location_state'])

    def __build_events_to_trigger_queue(self, day, event_states):
        """Build an ordered queue of events to trigger with the following properties:
        -- has not yet occurred AND
        -- is_daily OR is set to occur on the given day
        -- is ordered by time ascending, then is_daily=true, then is_daily=false
        (by having is_daily=True first, we can "overwrite" a daily event with a more specific one-day event at the same time)
        """
        untriggered_events = event_states.filter(has_occurred=False)

        events_to_trigger_queue = untriggered_events.filter(event__is_daily=True) | untriggered_events.filter(event__day=day)

        events_to_trigger_queue = events_to_trigger_queue.order_by('event__time', '-event__is_daily', 'event__pk')  # orders by time, then is_daily=True, then is_daily=False

        events_to_trigger_queue = events_to_trigger_queue.select_related('event__villagerappearsevent__villager', 'event__villagerappearsevent__place')

        return events_to_trigger_queue

    def trigger_event(self, event, session, villager_states, place_states):
        """Triggers the given event based on the event_type"""
        if event.event_type == ScheduledEvent.SHOP_POPULATES:
            return self.populate_shop(event.populateshopevent, session, place_states)  # django forces PopulateShopEvent into populateshopevent

        if event.event_type == ScheduledEvent.VILLAGER_APPEARS:
            return self.villager_appears(event.villagerappearsevent, villager_states, place_states)

    def populate_shop(self, event, session, place_states):
        """Fill the shop inventory for the day, which includes:
        -unlimited stock of a seed
        -limited gift (determined by items and gift quantity)
        -random merchandise (determined by merch_slots)"""

        item_tokens = []
        blocked_item_types = []

        content_configs = json.loads(event.content_config_list)

        for content_config in content_configs:
            print(content_config)
            item_name = content_config.get('item_name', None)
            quantity = content_config.get('quantity', None)
            merch_type = content_config.get('merch_type', None)

            if item_name:
                item = Item.objects.get_by_natural_key(item_name)
            elif merch_type:
                merch_slot = MerchSlot(merch_slot_type=merch_type)
                item = self.__pick_item_given_merch_slot(merch_slot, blocked_item_types)
                blocked_item_types.append(item.item_type)
            else:
                raise ValueError('Content config should have item_name or merch_type')

            item_token = ItemToken(session=session, item=item, quantity=quantity)
            item_tokens.append(item_token)

        ItemToken.objects.bulk_create(item_tokens)

        place_state = place_states.filter(place=event.shop).first()
        place_state.item_tokens.set(item_tokens)

    def __pick_item_given_merch_slot(self, merch_slot, blocked_item_types):
        allowed_item_types = list(set(merch_slot.potential_item_types) - set(blocked_item_types))
        item_type = random.choice(allowed_item_types)
        rarity = merch_slot.get_rarity(item_type)

        item = Item.objects.filter(item_type=item_type, rarity=rarity).order_by('?').first()

        return item

    def villager_appears(self, event, villager_states, place_states):
        villager_state = villager_states.filter(villager=event.villager).first()
        place_state = place_states.filter(place=event.place).first()

        villager_state.location_state = place_state

        return villager_state

    def reset_for_new_day(self, session):
        self.reset_villager_states(session.villager_states.all())
        self.reset_daily_events(session.event_states.all())
        self.grow_crops(session.place_states.all())

    def reset_villager_states(self, villager_states):
        villager_states.update(has_been_talked_to=False, has_been_given_gift=False)

    def reset_daily_events(self, event_states):
        event_states.filter(event__is_daily=True).update(has_occurred=False)

    def grow_crops(self, place_states):
        """Find all seeds/sprouts in the farm and "grow" them if they've been watered –
        ie replace them with a new item token at the next growth stage."""

        farm_state = next((state for state in place_states if state.place.place_type == FARM))
        item_tokens = farm_state.item_tokens.all()
        new_contents = []

        for token in item_tokens:
            if token.item_type not in [SEED, SPROUT] or not token.has_been_watered:
                new_contents.append(token)
                continue

            new_item = token.item.get_next_growth_stage()
            new_item_token = ItemToken.objects.create(session=farm_state.session, item=new_item)
            new_contents.append(new_item_token)

        farm_state.item_tokens.set(new_contents)

    def fall_asleep(self, clock, session):
        """Advances the clock to dawn or midday, depending on whether the hero is in bed or not,
        and returns a message"""
        hero_state = session.hero_state

        if clock.time > DAWN:
            raise Exception(f'Time on the new day should be before dawn, not {clock.time}')

        if hero_state.is_in_bed or session.location.is_farmhouse:
            hero_state.is_in_bed = False
            hero_state.save()

            clock.advance(clock.minutes_to_dawn)
            sleep_message = "You got a good night's sleep and wake up at dawn."
            is_error = False
        else:
            clock.advance(clock.minutes_to_overslept_time)
            sleep_message = "You passed out at midnight and overslept! You're just now waking up."
            is_error = True

        session.messages.create(text=sleep_message, is_error=is_error)

        clock.is_new_day = False
        clock.save()

    def trigger_game_over(self, session):
        hero_state = session.hero_state
        hero = session.hero

        is_new_high_score = hero.set_high_score(hero_state.score)

        if is_new_high_score:
            hero.boost_level += 1
            hero.save()

        end_of_game_message = self.get_end_of_game_message(hero_state, is_new_high_score)

        session.reset_session_state(end_of_game_message)

    def trigger_kys(self, session):
        session.reset_session_state(KYS_MESSAGE)

    def get_end_of_game_message(self, hero_state, is_new_high_score):
        start = f'You ended the week with {hero_state.koin_earned} koin and ' \
                f'{hero_state.hearts_earned} hearts for a total score of {hero_state.score}.'

        if is_new_high_score:
            middle = f"That's a new high score! Feeling your movements quicken slightly with the shifting of time," \

        else:
            middle = f"That doesn't beat your high score – but there's always next loop! "\
                       "Strengthened by the wisdom of experience," \

        end = "you enter the time loop to begin the week again."

        return f'{start} {middle} {end}'

    def __is_game_over(self, clock):
        return clock.is_new_day and clock.day == FIRST_DAY
