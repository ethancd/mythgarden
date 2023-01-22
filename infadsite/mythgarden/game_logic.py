from .models import Bridge, Action, Item, Villager, Place, Landmark

from .static_helpers import guard_type, guard_types


class ActionGenerator:
    def gen_available_actions(self, place, inventory, contents, villagers):
        """Returns a list of available actions for the hero in the current situation, taking into account:
        - the hero's current inventory
        - the location's current present items/occupants (contents and villagers)
        - the place's static features (landmarks and bridges)"""

        available_actions = []

        landmarks = place.landmarks.all()
        bridges = list(Bridge.objects.filter(place_1=place) | Bridge.objects.filter(place_2=place))

        if any([l.landmark_type == Landmark.FIELD for l in landmarks]):
            farming_actions = self.gen_farming_actions(contents, inventory)
            available_actions += farming_actions

        if any([l.landmark_type == Landmark.SHOP for l in landmarks]):
            shopping_actions = self.gen_shopping_actions(contents, inventory)
            available_actions += shopping_actions

        if len(bridges) > 0:
            travel_actions = self.gen_travel_actions(place, bridges)
            available_actions += travel_actions

        if len(villagers) > 0:
            social_actions = self.gen_social_actions(villagers, inventory)
            available_actions += social_actions

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
        gift_items = [i for i in inventory if i.item_type == Item.GIFT]

        for villager in villagers:
            actions.append(self.gen_talk_action(villager))

            for item in gift_items:
                actions.append(self.gen_give_action(item, villager))

        return actions

    def gen_give_action(self, item, villager):
        """Returns an action that gives passed item to passed villager"""
        return Action(
            description=f'Give {item.name} to {villager.name}',
            action_type=Action.GIV,
            target_object=villager,
            secondary_target_object=item,
            cost_amount=15,
            cost_unit=Action.MIN,
            log_statement=f'You gave a {item.name} to {villager.name}.',
        )

    def gen_talk_action(self, villager):
        """Returns an action that talks to given villager"""
        return Action(
            description=f'Talk to {villager.name}',
            action_type=Action.TAL,
            target_object=villager,
            cost_amount=1,
            cost_unit=Action.HOUR,
            log_statement=f'You talked to {villager.name}.',
        )

    def gen_sell_action(self, item):
        """Returns an action that sells given item"""
        return Action(
            description=f'Sell {item.name}',
            action_type=Action.SEL,
            target_object=item,
            cost_amount=-item.price,
            cost_unit=Action.KOIN,
            log_statement=f'You sold a {item.name} for {item.price} koin.',
        )

    def gen_buy_action(self, item):
        """Returns an action that buys given item"""
        return Action(
            description=f'Buy {item.name}',
            action_type=Action.BUY,
            target_object=item,
            cost_amount=item.price,
            cost_unit=Action.KOIN,
            log_statement=f'You bought a {item.name} for {item.price} koin.',
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
            cost_amount=1,
            cost_unit=Action.HOUR,
            log_statement=f'You watered the {sprout.name} sprouts.',
        )

    def gen_harvest_action(self, crop):
        """Returns an action that harvests given crop"""
        return Action(
            description=f'Harvest {crop.name}',
            action_type=Action.HAR,
            target_object=crop,
            cost_amount=1,
            cost_unit=Action.HOUR,
            log_statement=f'You harvested the {crop.name} crop.',
        )

    def gen_travel_action(self, destination, direction, display_direction):
        """Returns an action that travels to given destination in given direction"""
        return Action(
            description=f'Walk {display_direction}',
            action_type=Action.TRA,
            target_object=destination,
            direction=direction,
            cost_amount=1,
            cost_unit=Action.HOUR,
            log_statement=f'You travelled {display_direction} to {destination.name}.',
        )
