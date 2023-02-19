import random

from .models import Bridge, Action, Place, Building, Session, VillagerState, ItemToken, \
    DialogueLine, ScheduledEvent
from .models._constants import SEED, SPROUT, CROP, COMMON, UNCOMMON, RARE, EPIC, RARITIES, RARITY_WEIGHTS, FARM, SHOP, \
    WILD_TYPES, FOREST, MOUNTAIN, BEACH, LOVE, LIKE, NEUTRAL, DISLIKE, HATE, SUNDAY, DAWN, FISHING_DESCRIPTION, \
    DIGGING_DESCRIPTION, FORAGING_DESCRIPTION
from .static_helpers import guard_type, guard_types


def can_afford_action(wallet, requested_action):
    if requested_action.is_cost_in_money() and requested_action.action_type != Action.SELL:
        return wallet.money >= requested_action.cost_amount
    else:
        return True


class ActionGenerator:
    def gen_available_actions(self, place, inventory, contents, villager_states, clock):
        """Returns a list of available actions for the hero in the current session, taking into account:
        - the current inventory
        - the location's current present items/occupants (contents and villagers)
        - the place's static features (buildings and bridges)"""

        print(
            f'gen_available_actions: place={place}, inventory={inventory}, contents={contents}, villager_states={villager_states}, clock={clock}')
        available_actions = []

        buildings = list(place.buildings.all())
        bridges = list(Bridge.objects.filter(place_1=place) | Bridge.objects.filter(place_2=place))

        if place.place_type == FARM:
            available_actions += self.gen_farming_actions(contents, inventory)

        if place.place_type == SHOP:
            available_actions += self.gen_shopping_actions(contents, inventory)

        if place.place_type in WILD_TYPES:
            available_actions += self.gen_gather_actions(place)

        if len(buildings) > 0:
            available_actions += self.gen_enter_actions(buildings)

        try:
            building = place.building
            if building.surround is not None:
                available_actions += [self.gen_exit_action(building)]
        except Building.DoesNotExist:
            pass

        if len(bridges) > 0:
            available_actions += self.gen_travel_actions(place, bridges)

        if len(villager_states) > 0:
            available_actions += self.gen_social_actions(villager_states, inventory)

        if place.is_farmhouse:
            available_actions += [self.gen_sleep_action(clock)]

        return available_actions

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

        actions = []

        for villager_state in villager_states:
            villager = villager_state.villager
            if not villager_state.has_been_talked_to:
                actions.append(self.gen_talk_action(villager))

            if not villager_state.has_been_given_gift:
                for item_token in inventory:
                    actions.append(self.gen_give_action(item_token, villager))

        return actions

    def gen_give_action(self, item_token, villager):
        """Returns an action that gives passed item to passed villager"""
        return Action(
            description=f'Give {item_token.name} to {villager.name}',
            action_type=Action.GIVE,
            target_object=villager,
            secondary_target_object=item_token,
            cost_amount=5,
            cost_unit=Action.MIN,
            log_statement='You gave {item_name} to {villager_name}. Looks like they {valence_text}',
        )

    def gen_talk_action(self, villager):
        """Returns an action that talks to given villager"""

        return Action(
            description=f'Talk to {villager.name}',
            action_type=Action.TALK,
            target_object=villager,
            cost_amount=villager.talk_duration,
            cost_unit=Action.MIN,
            log_statement=f'You talked to {villager.name}.',
        )

    def gen_sell_action(self, item_token):
        """Returns an action that sells given item"""
        return Action(
            description=f'Sell {item_token.name}',
            action_type=Action.SELL,
            target_object=item_token,
            cost_amount=item_token.price,
            cost_unit=Action.KOIN,
            log_statement=f'You sold {item_token.name} for {item_token.price} koin.',
        )

    def gen_buy_action(self, item_token):
        """Returns an action that buys given item"""
        return Action(
            description=f'Buy {item_token.name}',
            action_type=Action.BUY,
            target_object=item_token,
            cost_amount=item_token.price,
            cost_unit=Action.KOIN,
            log_statement=f'You bought {item_token.name} for {item_token.price} koin.',
        )

    def gen_enter_action(self, building):
        """Returns an action that enters given building"""
        return Action(
            description=f'Enter {building.name}',
            action_type=Action.TRAVEL,
            target_object=building,
            cost_amount=5,
            cost_unit=Action.MIN,
            log_statement=f'You entered {building.name}.',
        )

    def gen_exit_action(self, building):
        """Returns an action that exits the current place"""
        return Action(
            description=f'Exit {building.name}',
            action_type=Action.TRAVEL,
            target_object=building.surround,
            cost_amount=5,
            cost_unit=Action.MIN,
            log_statement=f'You exited {building.name} back out to {building.surround.name}.',
        )

    def gen_plant_action(self, seed_token):
        """Returns an action that plants given seed"""
        return Action(
            description=f'Plant {seed_token.name}',
            action_type=Action.PLANT,
            target_object=seed_token,
            cost_amount=15,
            cost_unit=Action.MIN,
            log_statement=f'You planted some {seed_token.name} in the field.',
        )

    def gen_water_action(self, plant_token):
        """Returns an action that waters given seed/sprout"""
        return Action(
            description=f'Water {plant_token.name}',
            action_type=Action.WATER,
            target_object=plant_token,
            cost_amount=30,
            cost_unit=Action.MIN,
            log_statement=f'You watered the {plant_token.name}.',
        )

    def gen_harvest_action(self, crop_token):
        """Returns an action that harvests given crop"""
        return Action(
            description=f'Harvest {crop_token.name}',
            action_type=Action.HARVEST,
            target_object=crop_token,
            cost_amount=15,
            cost_unit=Action.MIN,
            log_statement=f'You harvested the {crop_token.name}.',
        )

    def gen_travel_action(self, destination, direction, display_direction):
        """Returns an action that travels to given destination in given direction"""
        return Action(
            description=f'Walk {display_direction}',
            action_type=Action.TRAVEL,
            target_object=destination,
            direction=direction,
            cost_amount=60,
            cost_unit=Action.MIN,
            log_statement=f'You travelled {display_direction} to {destination.name}.',
        )

    def gen_fishing_action(self):
        """Returns an action that catches a fish"""
        return Action(
            description=FISHING_DESCRIPTION,
            action_type=Action.GATHER,
            cost_amount=60,
            cost_unit=Action.MIN,
            log_statement='You caught a {result}!',
        )

    def gen_digging_action(self):
        """Returns an action that digs for minerals, gems, fossils, etc"""
        return Action(
            description=DIGGING_DESCRIPTION,
            action_type=Action.GATHER,
            cost_amount=90,
            cost_unit=Action.MIN,
            log_statement='You dug up a {result}!',
        )

    def gen_foraging_action(self):
        """Returns an action that forages for herbs, plants, etc"""
        return Action(
            description=FORAGING_DESCRIPTION,
            action_type=Action.GATHER,
            cost_amount=30,
            cost_unit=Action.MIN,
            log_statement='You found {result}!',
        )

    def gen_sleep_action(self, clock):
        """Returns an action for the hero to go to sleep till the next day"""
        return Action(
            description='Go to sleep',
            action_type=Action.SLEEP,
            cost_amount=clock.minutes_to_midnight,
            cost_unit=Action.MIN,
            log_statement='You tuck yourself into bed. Sweet dreams!',
        )


class ActionExecutor:
    def execute(self, action, session):
        """Executes the given action, modifying relevant models in the session, and returns updated
        (selecting the correct method based on the action type using a bit of meta programming, as a treat)"""
        guard_type(action, Action)
        guard_type(session, Session)

        ex = f'execute_{action.get_action_type_display().lower()}_action'

        if hasattr(self, ex) and callable(getattr(self, ex)):
            updated_models, log_statement = getattr(self, ex)(action, session)
        else:
            raise ValueError(f'Unknown action type: {action.get_action_type_display().lower()}')

        if session.message:
            log_statement = self.__append_session_message(log_statement, session)

        return updated_models, log_statement

    def execute_travel_action(self, action, session):
        """Executes a travel action, which updates the current location and ticks the clock"""

        session.location = action.target_object
        session.clock.advance(action.cost_amount)

        session.save_data()

        return ({
                    'place': session.location,
                    'clock': session.clock,
                    'buildings': list(session.location.buildings.all()),
                    'local_item_tokens': list(session.local_item_tokens.all()),
                    'villager_states': list(session.occupant_states.all())
                }, action.log_statement)

    def execute_talk_action(self, action, session):
        """Executes a talk action, which displays some dialogue, adds to the villager's affinity, and ticks the clock"""

        villager = action.target_object
        villager_state = session.get_villager_state(villager)

        dialogue = self.__get_dialogue_for_talk_action(villager_state, villager)
        hearts_gained = self.__update_affinity(villager_state, villager.friendliness, session.hero)

        session.hero.hearts_earned += hearts_gained
        session.clock.advance(action.cost_amount)
        villager_state.mark_as_talked_to()
        action.log_statement += self.__make_affinity_tag_if_any(hearts_gained, villager)

        villager_state.save()
        session.save_data()

        return ({
                    'hero': session.hero,
                    'clock': session.clock,
                    'villager_states': list(session.occupant_states.all()),
                    'dialogue': dialogue,
                }, action.log_statement)

    def execute_give_action(self, action, session):
        """Executes a give action, which removes an item from the hero's inventory
        and adds to the villager's affinity"""
        # also want to set villager_state to has_been_gifted so we can't talk to them again till tomorrow

        villager = action.target_object
        gift = action.secondary_target_object
        valence = villager.gift_valence(gift)
        affinity_amount = self.__calc_gift_affinity_change(valence, gift.rarity, villager.friendliness)

        villager_state = session.occupant_states.filter(villager=villager).first()
        villager_state.has_been_given_gift = True
        hearts_gained = self.__update_affinity(villager_state, affinity_amount, session.hero)

        session.hero.hearts_earned += hearts_gained

        villager_state.save()

        trigger = self.__get_gift_dialogue_trigger(valence)
        dialogue = villager.get_dialogue(trigger)

        session.clock.advance(action.cost_amount)
        session.inventory.item_tokens.remove(gift)

        session.save_data()

        valence_text = self.__get_valence_text(valence)
        log_statement = action.log_statement.format(item_name=gift.name, villager_name=villager.name,
                                                    valence_text=valence_text)

        log_statement += self.__make_affinity_tag_if_any(hearts_gained, villager)

        session.save_data()

        return ({
                    'hero': session.hero,
                    'inventory': list(session.inventory.item_tokens.all()),
                    'villager_states': list(session.occupant_states.all()),
                    'dialogue': dialogue,
                }, log_statement)

    def execute_sell_action(self, action, session):
        """Executes a sell action, which removes an item from the hero's inventory
        and adds the price in koin to the hero's wallet"""

        session.inventory.item_tokens.remove(action.target_object)
        session.wallet.money += action.cost_amount
        session.hero.koin_earned += action.cost_amount

        session.save_data()

        return ({
                    'hero': session.hero,
                    'wallet': session.wallet,
                    'inventory': list(session.inventory.item_tokens.all()),
                }, action.log_statement)

    def execute_buy_action(self, action, session):
        """Executes a buy action, which moves an item from the session contents into the hero's inventory
        and deducts the price in koin from the hero's wallet"""

        item = action.target_object

        session.inventory.item_tokens.add(item)
        session.location_state.item_tokens.remove(item)

        session.wallet.money -= action.cost_amount

        session.save_data()

        return ({
                    'wallet': session.wallet,
                    'inventory': list(session.inventory.item_tokens.all()),
                    'local_item_tokens': list(session.local_item_tokens.all()),
                }, action.log_statement)

    def execute_plant_action(self, action, session):
        """Executes a plant action, which moves a seed from the hero's inventory into the session contents"""

        session.inventory.item_tokens.remove(action.target_object)
        session.location_state.item_tokens.add(action.target_object)

        session.clock.advance(action.cost_amount)
        session.save_data()

        return ({
                    'clock': session.clock,
                    'inventory': list(session.inventory.item_tokens.all()),
                    'local_item_tokens': list(session.local_item_tokens.all()),
                }, action.log_statement)

    def execute_water_action(self, action, session):
        """Executes a water action, which sets the item_token's has_been_watered attribute to True"""

        item_token = action.target_object
        item_token.has_been_watered = True
        item_token.save()

        session.clock.advance(action.cost_amount)

        session.save_data()

        return ({
                    'clock': session.clock,
                    'local_item_tokens': list(session.local_item_tokens.all()),
                }, action.log_statement)

    def execute_harvest_action(self, action, session):
        """Executes a harvest action, which moves a crop from the session contents into the hero's inventory"""

        session.inventory.item_tokens.add(action.target_object)
        session.location_state.item_tokens.remove(action.target_object)

        session.clock.advance(action.cost_amount)

        session.save_data()

        return ({
                    'clock': session.clock,
                    'inventory': list(session.inventory.item_tokens.all()),
                    'local_item_tokens': list(session.local_item_tokens.all()),
                }, action.log_statement)

    def execute_gather_action(self, action, session):
        """Executes a gather action, which finds a random item in the current location's item pool
        and adds a copy to the hero's inventory"""

        item = self.__pull_item_from_pool(session.location)
        session.inventory.item_tokens.add(ItemToken.objects.create(session=session, item=item))
        session.clock.advance(action.cost_amount)

        session.save_data()

        log_statement = action.log_statement.format(result=item.name)

        return ({
                    'inventory': list(session.inventory.item_tokens.all()),
                    'clock': session.clock,
                }, log_statement)

    def execute_sleep_action(self, action, session):
        """Executes a sleep action, which advances the clock to midnight"""

        session.hero.is_in_bed = True
        session.clock.advance(action.cost_amount)

        session.save_data()

        return ({
                    'clock': session.clock,
                }, action.log_statement)

    # private methods
    def __get_dialogue_for_talk_action(self, villager_state, villager):
        if villager_state.has_ever_been_talked_to:
            trigger = DialogueLine.TALKED_TO
            affinity_tier = villager_state.affinity_tier
        else:
            trigger = DialogueLine.FIRST_MEETING
            affinity_tier = None

        return villager.get_dialogue(trigger, affinity_tier)

    def __append_session_message(self, log_statement, session):
        log_statement = log_statement + '\n' + session.message

        session.message = ''
        session.save()

        return log_statement

    def __pull_item_from_pool(self, location):
        """Returns a random item from the given location's item pool, weighted by rarity"""

        # Pick a rarity, find an item of that rarity;
        # if none found, try again with another rarity;
        # if no items at all, error out
        rarities = [r for r in RARITIES]
        while len(rarities) > 0:
            weights = [RARITY_WEIGHTS[r] for r in rarities]
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

    def __calc_gift_affinity_change(self, valence, rarity, friendliness):
        """Calculates the change in affinity for a gift based on valence of villager's reaction,
        item's rarity, villager's friendliness"""

        VALENCE_VALUE_MAP = {
            LOVE: 20,
            LIKE: 6,
            NEUTRAL: 2,
            DISLIKE: 0,
            HATE: -2,
        }

        RARITY_MULTIPLIER_MAP = {
            COMMON: 0.5,
            UNCOMMON: 1,
            RARE: 2,
            EPIC: 4,
        }

        base_value = VALENCE_VALUE_MAP[valence]
        multiplier = RARITY_MULTIPLIER_MAP[rarity]

        return int((base_value * multiplier) + friendliness)

    def __update_affinity(self, villager_state, amount, hero):
        """Updates the villager's villager_state affinity and returns the number of "hearts" gained (affinity tier diff)"""

        old_tier = villager_state.affinity_tier
        villager_state.add_affinity(amount)
        new_tier = villager_state.affinity_tier

        return new_tier - old_tier

        hero.hearts_earned += diff

        if diff > 0:
            return f' You and {villager.name} have developed more of a bond! +❤️'
        else:
            return ''

        return old_tier, new_tier

    def __make_affinity_tag_if_any(self, hearts_gained, villager):
        if hearts_gained > 0:
            hearts = ''.join(['❤️' for _ in range(hearts_gained)])
            return f" You and {villager.name} have developed more of a bond! +{hearts}"
        else:
            return ''

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

        # check for start of day and run hard-coded events
        if clock.is_new_day:
            self.reset_for_new_day(clock, session)

            session.message = self.fall_asleep(clock, session.hero)
            session.save()

        # run scheduled events (from database)
        self.trigger_scheduled_events(clock, list(session.event_states.all()), session)

    def reset_for_new_day(self, clock, session):
        clock.is_new_day = False
        clock.save()

        self.reset_villager_states(session.villager_states.all())

        self.grow_crops(session.place_states.get(place__place_type=FARM))

    def reset_villager_states(self, villager_states):
        villager_states.update(has_been_talked_to=False, has_been_given_gift=False)

    def grow_crops(self, farm_state):
        """Find all seeds/sprouts in the farm and "grow" them if they've been watered --
        ie replace them with a new item token at the next growth stage."""
        item_tokens = farm_state.item_tokens.all()
        new_contents = []

        for token in item_tokens:
            if token.item_type not in [SEED, SPROUT] or token.has_been_watered:
                new_contents.append(token)
                continue

            new_item = token.item.get_next_growth_stage()
            new_item_token = ItemToken.objects.create(session=farm_state.session, item=new_item)
            new_contents.append(new_item_token)

        farm_state.item_tokens.set(new_contents)

    def fall_asleep(self, clock, hero):
        """Advances the clock to dawn or midday, depending on whether the hero is in bed or not,
        and returns a message"""
        if clock.time > DAWN:
            raise Exception(f'Time on the new day should be before dawn, not {clock.time}')

        if hero.is_in_bed:
            hero.is_in_bed = False
            hero.save()
            clock.advance(clock.minutes_to_dawn)
            sleep_message = "You got a good night's sleep and wake up at dawn."
        else:
            clock.advance(clock.minutes_to_overslept_time)
            sleep_message = "You passed out at midnight and overslept! You're just now waking up."

        clock.save()
        return sleep_message

    def trigger_game_over(self, session):
        hero = session.hero
        end_of_game_message = f'You made it to the end of the week! You earned {hero.koin_earned} koin and ' \
                              f'{hero.hearts_earned} hearts, for a total score of {hero.score}. ' \
                              'Prepare to enter the time loop and start over again!'

        session.reset_session_state(end_of_game_message)

    def trigger_scheduled_events(self, clock, event_states, session):
        """Triggers all scheduled events that are due to occur at the current time"""

        for event_state in event_states:
            if self.__should_trigger(event_state, clock):
                self.trigger_event(event_state.event, session)
                event_state.mark_as_occurred()

    def trigger_event(self, event, session):
        """Triggers the given event based on the event_type"""
        if event.event_type == ScheduledEvent.ITEMS_APPEAR:
            self.make_items_appear(event, session)

    def make_items_appear(self, event, session):
        """Make items appear in the place saved on the event"""
        item_tokens = []
        for item in event.items.all():
            item_tokens.append(ItemToken(session=session, item=item))
        ItemToken.objects.bulk_create(item_tokens)

        place_state, created = session.place_states.get_or_create(place=event.place)

        place_state.item_tokens.set(item_tokens)

    # private methods
    def __should_trigger(self, event_state, clock):
        """Returns True if the event should be triggered, False otherwise"""
        event = event_state.event
        event_is_now_or_in_past = clock.is_now_or_in_past(event.day, event.time)

        return event_is_now_or_in_past and not event_state.has_occurred

    def __is_game_over(self, clock):
        return clock.is_new_day and clock.day == SUNDAY
