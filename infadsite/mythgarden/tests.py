from django.test import TestCase
from unittest.mock import MagicMock, patch
from django.core.validators import ValidationError

from .models import Item, Action, Villager, Place, Bridge, Landmark, Situation, Hero, Clock

from .game_logic import ActionGenerator, ActionExecutor


def assertAnyActionsOfType(actions, action_type):
    """Asserts that at least one action in the list of actions is of the given type"""
    for action in actions:
        if action.action_type == action_type:
            return
    raise AssertionError(f"No actions of type {action_type} found in {actions}")


def create_item(name='Rock', item_type=Item.GIFT, price=1):
    return Item.objects.create(name=name, item_type=item_type, price=price)


def create_villager(name='Lea', home=None):
    return Villager.objects.create(name=name, home=home)


def create_place(name='The Farm'):
    return Place.objects.create(name=name)


def create_bridge(place_1, place_2, direction_1=Bridge.WEST, direction_2=Bridge.EAST):
    return Bridge.objects.create(place_1=place_1, place_2=place_2, direction_1=direction_1, direction_2=direction_2)


def create_landmark(name, place, landmark_type):
    return Landmark.objects.create(name=name, place=place, landmark_type=landmark_type)


def create_hero(name='Stan'):
    return Hero.objects.create(name=name)


class GenAvailableActionsTests(TestCase):
    def setUp(self) -> None:
        self.ag = ActionGenerator()

        self.ag.gen_farming_actions = MagicMock()
        self.farming_actions = ['plant', 'water', 'harvest']
        self.ag.gen_farming_actions.return_value = self.farming_actions

        self.ag.gen_shopping_actions = MagicMock()
        self.shopping_actions = ['buy', 'sell']
        self.ag.gen_shopping_actions.return_value = self.shopping_actions

        self.ag.gen_travel_actions = MagicMock()
        self.travel_actions = ['walk']
        self.ag.gen_travel_actions.return_value = self.travel_actions

        self.ag.gen_social_actions = MagicMock()
        self.social_actions = ['talk', 'give']
        self.ag.gen_social_actions.return_value = self.social_actions

        self.farm = create_place('The Farm')
        self.inventory = []
        self.contents = []
        self.villagers = []

    def test_returns_list(self):
        """Returns a list"""
        actions = self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.assertIsInstance(actions, list)

    def test_calls_gen_farming_actions_when_place_has_field(self):
        """Calls gen_farming_actions when place has a field landmark"""
        create_landmark('Farm', self.farm, Landmark.FIELD)

        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_farming_actions.assert_called_once_with(self.contents, self.inventory)

    def test_returns_farming_actions_when_place_has_field(self):
        """Returns farming actions when place has a field landmark"""
        create_landmark('Farm', self.farm, Landmark.FIELD)

        actions = self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.assertEqual(actions, self.farming_actions)

    def test_does_not_call_gen_farming_actions_when_place_does_not_have_field(self):
        """Does not call gen_farming_actions when place is missing a field landmark"""
        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_farming_actions.assert_not_called()

    def test_calls_gen_shopping_actions_when_place_has_shop(self):
        """Calls gen_shopping_actions when place has a shop landmark"""
        create_landmark('Shop', self.farm, Landmark.SHOP)

        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_shopping_actions.assert_called_once_with(self.contents, self.inventory)

    def test_returns_shopping_actions_when_place_has_shop(self):
        """Returns shopping actions when place has a shop landmark"""
        create_landmark('Shop', self.farm, Landmark.SHOP)

        actions = self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.assertEqual(actions, self.shopping_actions)

    def test_does_not_call_gen_shopping_actions_when_place_does_not_have_shop(self):
        """Does not call gen_shopping_actions when place is missing a shop landmark"""
        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_shopping_actions.assert_not_called()

    def test_calls_gen_travel_actions_when_place_is_place_1_of_a_saved_bridge(self):
        """Calls gen_travel_actions when place is place_1 of a bridge"""
        bridges = [create_bridge(self.farm, create_place('The Forest'))]

        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_travel_actions.assert_called_once_with(self.farm, bridges)

    def test_returns_travel_actions_when_place_is_place_1_of_a_saved_bridge(self):
        """Returns travel actions when place is place_1 of a bridge"""
        create_bridge(self.farm, create_place('The Forest'))

        actions = self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.assertEqual(actions, self.travel_actions)

    def test_calls_gen_travel_actions_when_place_is_place_2_of_a_saved_bridge(self):
        """Calls gen_travel_actions when place is place_2 of a bridge"""
        bridges = [create_bridge(create_place('The Forest'), self.farm)]

        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_travel_actions.assert_called_once_with(self.farm, bridges)

    def test_calls_gen_travel_actions_when_place_is_part_of_multiple_bridges(self):
        """Calls gen_travel_actions when place is part of multiple bridges"""
        bridges = [
            create_bridge(self.farm, create_place('The Forest')),
            create_bridge(create_place('The Mountains'), self.farm)
        ]

        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_travel_actions.assert_called_once_with(self.farm, bridges)

    def test_does_not_call_gen_travel_actions_when_place_is_not_in_a_saved_bridge(self):
        """Does not call gen_travel_actions when place is not a bridge"""
        create_bridge(create_place('The Forest'), create_place('The Mountains'))

        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_travel_actions.assert_not_called()

    def test_calls_gen_social_actions_when_villagers_are_present(self):
        """Calls gen_social_actions when villagers are present"""
        self.villagers = [create_villager()]

        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_social_actions.assert_called_once_with(self.villagers, self.inventory)

    def test_returns_social_actions_when_villagers_are_present(self):
        """Returns social actions when villagers are present"""
        self.villagers = [create_villager()]

        actions = self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.assertEqual(actions, self.social_actions)

    def test_does_not_call_gen_social_actions_when_no_villagers_are_present(self):
        """Does not call gen_social_actions when no villagers are present"""
        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_social_actions.assert_not_called()

    def test_returns_multiple_types_of_actions_when_multiple_types_are_available(self):
        """Returns multiple types of actions when multiple types are available"""
        create_landmark('Field', self.farm, Landmark.FIELD)
        create_bridge(self.farm, create_place('The Forest'))
        self.villagers = [create_villager()]

        actions = self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.assertEqual(actions, self.farming_actions + self.travel_actions + self.social_actions)


class GenShoppingActionsTests(TestCase):
    def setUp(self) -> None:
        self.ag = ActionGenerator()
        self.shop_contents = []
        self.inventory = []

    def test_returns_list(self):
        """
        Returns a list
        """
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertIsInstance(actions, list)

    def test_returns_empty_list_if_no_shop_contents_and_no_inventory(self):
        """
        Returns an empty list if there are no contents and no inventory
        """
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions, [])

    def test_returns_buy_actions_if_shop_contents_and_no_inventory(self):
        """
        Returns a list with only buy actions if there are shop_contents but no inventory
        """
        self.shop_contents = [create_item() for _ in range(3)]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        for i in range(len(actions)):
            self.assertEqual(actions[i].action_type, Action.BUY)

    def test_returns_sell_actions_if_inventory_and_no_shop_contents(self):
        """
        Returns a list with only sell actions if there is inventory but no shop_contents
        """
        self.inventory = [create_item() for _ in range(3)]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        for i in range(len(actions)):
            self.assertEqual(actions[i].action_type, Action.SEL)

    def test_returns_buy_and_sell_actions_if_shop_contents_and_inventory(self):
        """
        Returns a list with both buy and sell actions if there are shop_contents and inventory
        """
        self.shop_contents = [create_item() for _ in range(2)]
        self.inventory = [create_item() for _ in range(2)]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        assertAnyActionsOfType(actions, Action.BUY)
        assertAnyActionsOfType(actions, Action.SEL)

        for i in range(len(actions)):
            self.assertIn(actions[i].action_type, [Action.BUY, Action.SEL])

    def test_returns_buy_actions_with_correct_description(self):
        """
        Returns a list with buy actions with the correct description
        """
        self.shop_contents = [create_item(name='Rock')]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].description, 'Buy Rock')

    def test_returns_buy_actions_with_correct_log_statement(self):
        """
        Returns a list with buy actions with the correct log_statement
        """
        self.shop_contents = [create_item(name='Rock', price=5)]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].log_statement, 'You bought a Rock for 5 koin.')

    def test_returns_buy_actions_with_correct_target_object(self):
        """
        Returns a list with buy actions with the correct target_object
        """
        self.shop_contents = [create_item()]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].target_object, self.shop_contents[0])

    def test_returns_buy_actions_with_correct_price(self):
        """
        Returns a list with buy actions with the correct cost_amount
        """
        self.shop_contents = [create_item(price=5)]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].cost_amount, 5)

    def test_returns_buy_actions_with_correct_cost_unit(self):
        """
        Returns a list with buy actions with the correct cost_unit
        """
        self.inventory = [create_item()]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].cost_unit, Action.KOIN)

    def test_returns_sell_actions_with_correct_description(self):
        """
        Returns a list with sell actions with the correct description
        """
        self.inventory = [create_item(name='Rock')]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].description, 'Sell Rock')

    def test_returns_sell_actions_with_correct_log_statement(self):
        """
        Returns a list with sell actions with the correct log_statement
        """
        self.inventory = [create_item(name='Rock', price=5)]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].log_statement, 'You sold a Rock for 5 koin.')

    def test_returns_sell_actions_with_correct_target_object(self):
        """
        Returns a list with sell actions with the correct target_object
        """
        self.inventory = [create_item()]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].target_object, self.inventory[0])

    def test_returns_sell_actions_with_correct_price(self):
        """
        Returns a list with sell actions with the correct cost_amount,
        which is negative the item's price
        """
        self.inventory = [create_item(price=5)]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].cost_amount, 5)

    def test_returns_sell_actions_with_correct_cost_unit(self):
        """
        Returns a list with sell actions with the correct cost_unit
        """
        self.inventory = [create_item()]
        actions = self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

        self.assertEqual(actions[0].cost_unit, Action.KOIN)

    def test_throws_an_error_if_passed_shop_contents_with_non_items(self):
        """
        Throws an error if passed a shop_contents with non-Item objects
        """
        self.shop_contents = [create_item(), 'Rock']
        self.inventory = [create_item()]

        with self.assertRaises(TypeError):
            self.ag.gen_shopping_actions(self.shop_contents, self.inventory)

    def test_throws_an_error_if_passed_inventory_with_non_items(self):
        """
        Throws an error if passed an inventory with non-Item objects
        """
        self.shop_contents = [create_item()]
        self.inventory = [create_item(), 'Rock']

        with self.assertRaises(TypeError):
            self.ag.gen_shopping_actions(self.shop_contents, self.inventory)


class GenSocialActionsTests(TestCase):
    def setUp(self):
        self.ag = ActionGenerator()
        self.villagers = []
        self.inventory = []

    def test_returns_list(self):
        """
        Returns a list
        """
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        self.assertIsInstance(actions, list)

    def test_returns_empty_list_if_no_villagers(self):
        """
        Returns an empty list if there are no villagers
        """
        self.inventory = [create_item()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        self.assertEqual(actions, [])

    def test_returns_talk_actions_if_villagers_and_no_inventory(self):
        """
        Returns a list with only talk actions if there are villagers but no inventory
        """
        self.villagers = [create_villager(name='Lea'), create_villager(name='Graham')]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        for i in range(len(actions)):
            self.assertEqual(actions[i].action_type, Action.TAL)

    def test_returns_talk_actions_and_gift_actions_if_villagers_and_inventory(self):
        """
        Returns a list with both talk and gift actions if there are villagers and inventory
        """
        self.villagers = [create_villager(name='Lea'), create_villager(name='Graham')]
        self.inventory = [create_item()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        assertAnyActionsOfType(actions, Action.TAL)
        assertAnyActionsOfType(actions, Action.GIV)

        for i in range(len(actions)):
            self.assertIn(actions[i].action_type, [Action.TAL, Action.GIV])

    def test_returns_one_talk_action_per_villager(self):
        """
        Returns one talk action per villager
        """
        self.villagers = [create_villager(name='Lea'), create_villager(name='Graham'), create_villager(name='Suki')]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        talk_actions = [a for a in actions if a.action_type == Action.TAL]

        self.assertEqual(len(talk_actions), 3)

    def test_returns_m_times_n_gift_actions(self):
        """
        Returns m times n gift actions, where m is the number of villagers and n is the number of items
        """
        self.villagers = [create_villager(name='Lea'), create_villager(name='Graham'), create_villager(name='Suki')]
        self.inventory = [create_item(), create_item()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        gift_actions = [a for a in actions if a.action_type == Action.GIV]

        self.assertEqual(len(gift_actions), 6)

    def test_returns_talk_actions_with_correct_description(self):
        """
        Returns a list with talk actions with the correct description
        """
        self.villagers = [create_villager(name='Lea')]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        self.assertEqual(actions[0].description, 'Talk to Lea')

    def test_returns_talk_actions_with_correct_log_statement(self):
        """
        Returns a list with talk actions with the correct log_statement
        """
        self.villagers = [create_villager(name='Lea')]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        self.assertEqual(actions[0].log_statement, 'You talked to Lea.')

    def test_returns_talk_actions_with_correct_target_object(self):
        """
        Returns a list with talk actions with the correct villager as target_object
        """
        self.villagers = [create_villager()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        self.assertEqual(actions[0].target_object, self.villagers[0])

    def test_returns_talk_actions_with_correct_cost_amount(self):
        """
        Returns a list with talk actions with the correct cost_amount
        """
        self.villagers = [create_villager()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        self.assertEqual(actions[0].cost_amount, 1)

    def test_returns_talk_actions_with_correct_cost_unit(self):
        """
        Returns a list with talk actions with the correct cost_unit
        """
        self.villagers = [create_villager()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        self.assertEqual(actions[0].cost_unit, Action.HOUR)

    def test_returns_gift_actions_with_correct_description(self):
        """
        Returns a list with gift actions with the correct description
        """
        self.villagers = [create_villager(name='Lea')]
        self.inventory = [create_item(name='Rock')]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        gift_action = [a for a in actions if a.action_type == Action.GIV][0]

        self.assertEqual(gift_action.description, 'Give Rock to Lea')

    def test_returns_gift_actions_with_correct_log_statement(self):
        """
        Returns a list with gift actions with the correct log_statement
        """
        self.villagers = [create_villager(name='Lea')]
        self.inventory = [create_item(name='Rock')]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        gift_action = [a for a in actions if a.action_type == Action.GIV][0]

        self.assertEqual(gift_action.log_statement, 'You gave a Rock to Lea.')

    def test_returns_gift_actions_with_correct_target_object(self):
        """
        Returns a list with gift actions with the correct villager as target_object
        """
        self.villagers = [create_villager()]
        self.inventory = [create_item()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        gift_action = [a for a in actions if a.action_type == Action.GIV][0]

        self.assertEqual(gift_action.target_object, self.villagers[0])

    def test_returns_gift_actions_with_correct_secondary_target_object(self):
        """
        Returns a list with gift actions with the correct item as secondary_target_object
        """
        self.villagers = [create_villager()]
        self.inventory = [create_item()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        gift_action = [a for a in actions if a.action_type == Action.GIV][0]

        self.assertEqual(gift_action.secondary_target_object, self.inventory[0])

    def test_returns_gift_actions_with_correct_cost_amount(self):
        """
        Returns a list with gift actions with the correct cost_amount
        """
        self.villagers = [create_villager()]
        self.inventory = [create_item()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        gift_action = [a for a in actions if a.action_type == Action.GIV][0]

        self.assertEqual(gift_action.cost_amount, 15)

    def test_returns_gift_actions_with_correct_cost_unit(self):
        """
        Returns a list with gift actions with the correct cost_unit
        """
        self.villagers = [create_villager()]
        self.inventory = [create_item()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        gift_action = [a for a in actions if a.action_type == Action.GIV][0]

        self.assertEqual(gift_action.cost_unit, Action.MIN)

    def test_throws_an_error_if_passed_non_villagers(self):
        """
        Throws an error if passed non-villagers
        """
        self.villagers = [create_item()]
        self.inventory = [create_item()]

        with self.assertRaises(TypeError):
            self.ag.gen_social_actions(self.villagers, self.inventory)

    def test_throws_an_error_if_passed_non_items(self):
        """
        Throws an error if passed non-items
        """
        self.villagers = [create_villager()]
        self.inventory = ['Rock']

        with self.assertRaises(TypeError):
            self.ag.gen_social_actions(self.villagers, self.inventory)


class GenFarmingActionsTests(TestCase):
    def setUp(self) -> None:
        self.ag = ActionGenerator()
        self.field_contents = []
        self.inventory = []

    def test_returns_a_list(self):
        """
        Returns a list
        """
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        self.assertIsInstance(actions, list)

    def test_returns_empty_list_when_field_and_inventory_are_empty(self):
        """
        Returns an empty list when field and inventory are empty
        """
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        self.assertEqual(actions, [])

    def test_returns_plant_actions_when_inventory_has_seeds(self):
        """
        Returns plant actions when inventory has seeds
        """
        self.inventory = [
            create_item(name='Parsnip', item_type=Item.SEED),
            create_item(name='Strawberry', item_type=Item.SEED),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        for i in range(len(actions)):
            self.assertEqual(actions[i].action_type, Action.PLA)

    def test_returns_plant_actions_with_correct_description(self):
        """
        Returns a list with plant actions with the correct description
        """
        self.inventory = [create_item(name='Parsnip', item_type=Item.SEED)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        plant_action = [a for a in actions if a.action_type == Action.PLA][0]

        self.assertEqual(plant_action.description, 'Plant Parsnip')

    def test_returns_plant_actions_with_correct_log_statement(self):
        """
        Returns a list with plant actions with the correct log_statement
        """
        self.inventory = [create_item(name='Parsnip', item_type=Item.SEED)]

        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)
        plant_action = [a for a in actions if a.action_type == Action.PLA][0]

        self.assertEqual(plant_action.log_statement, 'You planted some Parsnip in the field.')

    def test_returns_plant_actions_with_correct_target_object(self):
        """
        Returns a list with plant actions with the correct item as target_object
        """
        self.inventory = [create_item(name='Parsnip', item_type=Item.SEED)]

        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)
        plant_action = [a for a in actions if a.action_type == Action.PLA][0]

        self.assertEqual(plant_action.target_object, self.inventory[0])

    def test_returns_plant_actions_with_correct_cost_amount(self):
        """
        Returns a list with plant actions with the correct cost_amount
        """
        self.inventory = [create_item(name='Parsnip', item_type=Item.SEED)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        plant_action = [a for a in actions if a.action_type == Action.PLA][0]

        self.assertEqual(plant_action.cost_amount, 30)

    def test_returns_plant_actions_with_correct_cost_unit(self):
        """
        Returns a list with plant actions with the correct cost_unit
        """
        self.inventory = [create_item(name='Parsnip', item_type=Item.SEED)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        plant_action = [a for a in actions if a.action_type == Action.PLA][0]

        self.assertEqual(plant_action.cost_unit, Action.MIN)

    def test_returns_water_actions_when_field_has_sprouts(self):
        """
        Returns water actions when field has sprouts
        """
        self.field_contents = [
            create_item(name='Parsnip', item_type=Item.SPROUT),
            create_item(name='Strawberry', item_type=Item.SPROUT),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        for i in range(len(actions)):
            self.assertEqual(actions[i].action_type, Action.WAT)

    def test_returns_water_actions_with_correct_description(self):
        """
        Returns a list with water actions with the correct description
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.SPROUT)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        water_action = [a for a in actions if a.action_type == Action.WAT][0]

        self.assertEqual(water_action.description, 'Water Parsnip')

    def test_returns_water_actions_with_correct_log_statement(self):
        """
        Returns a list with water actions with the correct log_statement
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.SPROUT)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        water_action = [a for a in actions if a.action_type == Action.WAT][0]

        self.assertEqual(water_action.log_statement, 'You watered the Parsnip sprouts.')

    def test_returns_water_actions_with_correct_target_object(self):
        """
        Returns a list with water actions with the correct item as target_object
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.SPROUT)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        water_action = [a for a in actions if a.action_type == Action.WAT][0]

        self.assertEqual(water_action.target_object, self.field_contents[0])

    def test_returns_water_actions_with_correct_cost_amount(self):
        """
        Returns a list with water actions with the correct cost_amount
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.SPROUT)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        water_action = [a for a in actions if a.action_type == Action.WAT][0]

        self.assertEqual(water_action.cost_amount, 1)

    def test_returns_water_actions_with_correct_cost_unit(self):
        """
        Returns a list with water actions with the correct cost_unit
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.SPROUT)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        water_action = [a for a in actions if a.action_type == Action.WAT][0]

        self.assertEqual(water_action.cost_unit, Action.HOUR)

    def test_returns_harvest_actions_when_field_has_crops(self):
        """
        Returns harvest actions when field has crops
        """
        self.field_contents = [
            create_item(name='Parsnip', item_type=Item.CROP),
            create_item(name='Strawberry', item_type=Item.CROP),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        for i in range(len(actions)):
            self.assertEqual(actions[i].action_type, Action.HAR)

    def test_returns_harvest_actions_with_correct_description(self):
        """
        Returns a list with harvest actions with the correct description
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.CROP)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        harvest_action = [a for a in actions if a.action_type == Action.HAR][0]

        self.assertEqual(harvest_action.description, 'Harvest Parsnip')

    def test_returns_harvest_actions_with_correct_log_statement(self):
        """
        Returns a list with harvest actions with the correct log_statement
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.CROP)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        harvest_action = [a for a in actions if a.action_type == Action.HAR][0]

        self.assertEqual(harvest_action.log_statement, 'You harvested the Parsnip crop.')

    def test_returns_harvest_actions_with_correct_target_object(self):
        """
        Returns a list with harvest actions with the correct item as target_object
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.CROP)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        harvest_action = [a for a in actions if a.action_type == Action.HAR][0]

        self.assertEqual(harvest_action.target_object, self.field_contents[0])

    def test_returns_harvest_actions_with_correct_cost_amount(self):
        """
        Returns a list with harvest actions with the correct cost_amount
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.CROP)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        harvest_action = [a for a in actions if a.action_type == Action.HAR][0]

        self.assertEqual(harvest_action.cost_amount, 1)

    def test_returns_harvest_actions_with_correct_cost_unit(self):
        """
        Returns a list with harvest actions with the correct cost_unit
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.CROP)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        harvest_action = [a for a in actions if a.action_type == Action.HAR][0]

        self.assertEqual(harvest_action.cost_unit, Action.HOUR)

    def test_returns_plant_and_water_actions_when_there_are_seeds_and_sprouts(self):
        """
        Returns plant and water actions when there are seeds and sprouts
        """
        self.field_contents = [
            create_item(name='Parsnip', item_type=Item.SPROUT),
            create_item(name='Strawberry', item_type=Item.SPROUT),
        ]
        self.inventory = [
            create_item(name='Parsnip', item_type=Item.SEED),
            create_item(name='Strawberry', item_type=Item.SEED),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        assertAnyActionsOfType(actions, Action.PLA)
        assertAnyActionsOfType(actions, Action.WAT)

        for i in range(len(actions)):
            self.assertIn(actions[i].action_type, [Action.PLA, Action.WAT])

    def test_returns_water_and_harvest_actions_when_there_are_sprouts_and_crops(self):
        """
        Returns water and harvest actions when there are sprouts and crops
        """
        self.field_contents = [
            create_item(name='Parsnip', item_type=Item.SPROUT),
            create_item(name='Strawberry', item_type=Item.CROP),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        assertAnyActionsOfType(actions, Action.WAT)
        assertAnyActionsOfType(actions, Action.HAR)

        for i in range(len(actions)):
            self.assertIn(actions[i].action_type, [Action.WAT, Action.HAR])

    def test_returns_plant_and_harvest_actions_when_there_are_seeds_and_crops(self):
        """
        Returns plant and harvest actions when there are seeds and crops
        """
        self.field_contents = [
            create_item(name='Parsnip', item_type=Item.CROP),
            create_item(name='Strawberry', item_type=Item.CROP),
        ]
        self.inventory = [
            create_item(name='Parsnip', item_type=Item.SEED),
            create_item(name='Strawberry', item_type=Item.SEED),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        plant_actions = [a for a in actions if a.action_type == Action.PLA]
        harvest_actions = [a for a in actions if a.action_type == Action.HAR]

        self.assertEqual(len(plant_actions), 2)
        self.assertEqual(len(harvest_actions), 2)

    def test_returns_plant_and_water_and_harvest_actions_when_there_are_seeds_sprouts_and_crops(self):
        """
        Returns plant, water and harvest actions when there are seeds, sprouts and crops
        """
        self.field_contents = [
            create_item(name='Parsnip', item_type=Item.SPROUT),
            create_item(name='Strawberry', item_type=Item.CROP),
        ]
        self.inventory = [
            create_item(name='Parsnip', item_type=Item.SEED),
            create_item(name='Strawberry', item_type=Item.SEED),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        assertAnyActionsOfType(actions, Action.PLA)
        assertAnyActionsOfType(actions, Action.WAT)
        assertAnyActionsOfType(actions, Action.HAR)

        for i in range(len(actions)):
            self.assertIn(actions[i].action_type, [Action.PLA, Action.WAT, Action.HAR])

    def test_does_not_return_plant_actions_when_seeds_are_only_in_field_contents(self):
        """
        Does not return plant actions when seeds are only in field_contents and not in the inventory
        """
        self.field_contents = [
            create_item(name='Parsnip', item_type=Item.SEED),
            create_item(name='Strawberry', item_type=Item.SEED),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        plant_actions = [a for a in actions if a.action_type == Action.PLA]

        self.assertEqual(len(plant_actions), 0)

    def test_does_not_return_water_actions_when_sprouts_are_only_in_inventory(self):
        """
        Does not return water actions when sprouts are only in inventory and not in the field contents
        """
        self.inventory = [
            create_item(name='Parsnip', item_type=Item.SPROUT),
            create_item(name='Strawberry', item_type=Item.SPROUT),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        water_actions = [a for a in actions if a.action_type == Action.WAT]

        self.assertEqual(len(water_actions), 0)

    def test_does_not_return_harvest_actions_when_crops_are_only_in_inventory(self):
        """
        Does not return harvest actions when crops are only in inventory and not in the field contents
        """
        self.inventory = [
            create_item(name='Parsnip', item_type=Item.CROP),
            create_item(name='Strawberry', item_type=Item.CROP),
        ]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        harvest_actions = [a for a in actions if a.action_type == Action.HAR]

        self.assertEqual(len(harvest_actions), 0)

    def test_throws_error_if_passed_non_items_in_field_contents(self):
        """
        Throws error if passed non-items in field_contents
        """
        self.field_contents = [
            create_item(name='Parsnip', item_type=Item.SPROUT),
            'Strawberry',
        ]

        with self.assertRaises(TypeError):
            self.ag.gen_farming_actions(self.field_contents, self.inventory)

    def test_throws_error_if_passed_non_items_in_inventory(self):
        """
        Throws error if passed non-items in inventory
        """
        self.inventory = [
            create_item(name='Parsnip', item_type=Item.SPROUT),
            'Strawberry',
        ]

        with self.assertRaises(TypeError):
            self.ag.gen_farming_actions(self.field_contents, self.inventory)


class GenTravelActionsTests(TestCase):
    def setUp(self):
        self.ag = ActionGenerator()
        self.farm = create_place(name='The Farm')
        self.store = create_place(name='The Store')
        self.beach = create_place(name='The Beach')
        self.bridges = []
        
    def test_returns_list(self):
        """
        Returns a list
        """
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertIsInstance(actions, list)

    def test_returns_empty_list_if_no_bridges(self):
        """
        Returns an empty list if there are no bridges
        """
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions, [])

    def test_throws_an_error_if_place_is_missing(self):
        """
        Throws an error if place is missing
        """
        self.bridges = [create_bridge(self.farm, self.store)]

        with self.assertRaises(TypeError):
            self.ag.gen_travel_actions(None, self.bridges)

    def test_throws_an_error_if_bridges_has_non_bridges(self):
        """
        Throws an error if bridges has non-bridges
        """
        self.bridges = [create_bridge(self.farm, self.store), 'Bridge to The Beach']

        with self.assertRaises(TypeError):
            self.ag.gen_travel_actions(self.farm, self.bridges)

    def test_returns_one_travel_action_for_each_bridge(self):
        """
        Returns a travel action for each bridge
        """
        self.bridges = [
            create_bridge(self.farm, self.store),
            create_bridge(self.farm, self.beach, Bridge.NORTH, Bridge.SOUTH),
        ]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        travel_actions = [a for a in actions if a.action_type == Action.TRA]

        self.assertEqual(len(travel_actions), 2)

    def test_returns_travel_actions_with_correct_description(self):
        """
        Returns travel actions with the correct description
        """
        self.bridges = [create_bridge(self.farm, self.store, Bridge.WEST, Bridge.EAST)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].description, 'Walk East')

    def test_returns_travel_actions_with_correct_log_statement(self):
        """
        Returns travel actions with the correct log statement
        """
        self.bridges = [create_bridge(self.farm, self.store, Bridge.WEST, Bridge.EAST)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].log_statement, 'You travelled East to The Store.')

    def test_returns_travel_actions_with_correct_direction(self):
        """
        Returns travel actions with the correct direction
        """
        self.bridges = [create_bridge(self.farm, self.store, Bridge.WEST, Bridge.EAST)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].direction, Bridge.EAST)

    def test_returns_travel_actions_with_correct_destination(self):
        """
        Returns travel actions with the correct destination
        """
        self.bridges = [create_bridge(self.farm, self.store, Bridge.WEST, Bridge.EAST)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].target_object, self.store)

    def test_returns_travel_actions_with_correct_cost_amount(self):
        """
        Returns travel actions with the correct cost amount
        """
        self.bridges = [create_bridge(self.farm, self.store)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].cost_amount, 1)

    def test_returns_travel_actions_with_correct_cost_unit(self):
        """
        Returns travel actions with the correct cost unit
        """
        self.bridges = [create_bridge(self.farm, self.store)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].cost_unit, Action.HOUR)

    def test_returns_travel_actions_with_correct_direction_when_place_is_place_2_on_the_bridge(self):
        """
        Returns travel actions with the correct direction
        when the current place is stored as place 2 on the bridge
        """
        self.bridges = [create_bridge(self.store, self.farm, Bridge.EAST, Bridge.WEST)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].direction, Bridge.EAST)

    def test_returns_travel_actions_with_correct_description_when_place_is_place_2_on_the_bridge(self):
        """
        Returns travel actions with the correct description
        when the current place is stored as place 2 on the bridge
        """
        self.bridges = [create_bridge(self.store, self.farm, Bridge.EAST, Bridge.WEST)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].description, 'Walk East')

    def test_returns_travel_actions_with_correct_log_statement_when_place_is_place_2_on_the_bridge(self):
        """
        Returns travel actions with the correct log statement
        when the current place is stored as place 2 on the bridge
        """
        self.bridges = [create_bridge(self.store, self.farm, Bridge.EAST, Bridge.WEST)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].log_statement, 'You travelled East to The Store.')


class ActionModelTests(TestCase):
    def test_computes_correct_display_cost_for_time_actions(self):
        """
        Computes the correct display cost for time actions
        """
        action = Action(action_type=Action.WAT, cost_amount=1, cost_unit=Action.HOUR)

        self.assertEqual(action.display_cost, '1h')

    def test_computes_correct_display_cost_for_money_actions(self):
        """
        Computes the correct display cost for money actions
        """
        action = Action(action_type=Action.BUY, cost_amount=5, cost_unit=Action.KOIN)

        self.assertEqual(action.display_cost, '₭5')


class PlaceModelTests(TestCase):
    def setUp(self):
        self.place = create_place()

    def test_if_has_field_landmark_cannot_add_second_field_landmark(self):
        """
        If a place has a field landmark, cannot add a second field landmark
        """
        create_landmark('Field 1', self.place, Landmark.FIELD)

        with self.assertRaises(ValidationError):
            create_landmark('Field 2', self.place, Landmark.FIELD)

    def test_if_has_field_landmark_cannot_add_shop_landmark(self):
        """
        If a place has a field landmark, cannot add a shop landmark
        """
        create_landmark('Field 1', self.place, Landmark.FIELD)

        with self.assertRaises(ValidationError):
            create_landmark('Micro Shop', self.place, Landmark.SHOP)

    def test_if_has_shop_landmark_cannot_add_field_landmark(self):
        """
        If a place has a shop landmark, cannot add a field landmark
        """
        create_landmark('Micro Shop', self.place, Landmark.SHOP)

        with self.assertRaises(ValidationError):
            create_landmark('Field 1', self.place, Landmark.FIELD)

    def test_if_has_shop_landmark_cannot_add_second_shop_landmark(self):
        """
        If a place has a shop landmark, cannot add a second shop landmark
        """
        create_landmark('Micro Shop', self.place, Landmark.SHOP)

        with self.assertRaises(ValidationError):
            create_landmark('Secondary Micro Shop', self.place, Landmark.SHOP)


class ClockModelTests(TestCase):
    def setUp(self):
        self.clock = Clock(hero=create_hero(), day=Clock.MONDAY, time=9)

    def test_parse_duration_returns_a_float(self):
        """
        parse_duration returns a float
        """
        duration = 1
        unit = Action.HOUR

        amount = self.clock.parse_duration(duration, unit)

        self.assertTrue(isinstance(amount, float))

    def test_parse_duration_returns_correct_amount_for_hours(self):
        """
        parse_duration returns the correct amount for hours
        """
        duration = 1
        unit = Action.HOUR

        amount = self.clock.parse_duration(duration, unit)

        self.assertEqual(amount, 1.0)

    def test_parse_duration_returns_correct_amount_for_minutes(self):
        """
        parse_duration returns the correct amount for minutes
        """
        duration = 30
        unit = Action.MIN

        amount = self.clock.parse_duration(duration, unit)

        self.assertEqual(amount, 0.5)

    def test_parse_duration_returns_correct_amount_for_days(self):
        """
        parse_duration returns the correct amount for days
        """
        duration = 2
        unit = Action.DAY

        amount = self.clock.parse_duration(duration, unit)

        self.assertEqual(amount, 48.0)

    def test_parse_duration_throws_error_for_invalid_unit(self):
        """
        parse_duration throws an error for an invalid unit
        """
        duration = 1
        unit = 'q'

        with self.assertRaises(ValueError):
            self.clock.parse_duration(duration, unit)

    def test_advance_should_advance_the_time_by_the_amount_of_hours(self):
        """
        advance should advance the time by the amount of hours
        """
        self.clock.time = 9
        self.clock.advance(1, Action.HOUR)

        self.assertEqual(self.clock.time, 10)

    def test_advance_should_roll_time_over_when_time_equals_24(self):
        """
        advance should roll time over when time equals 24
        """
        self.clock.time = 9
        self.clock.advance(15, Action.HOUR)

        self.assertEqual(self.clock.time, 0)

    def test_advance_should_roll_time_over_when_time_exceeds_24(self):
        """
        advance should roll time over when time exceeds 24
        """
        self.clock.time = 9
        self.clock.advance(18, Action.HOUR)

        self.assertEqual(self.clock.time, 3)

    def test_advance_should_roll_day_over_when_time_exceeds_24(self):
        """
        advance should roll day over when time exceeds 24
        """
        self.clock.day = Clock.MONDAY
        self.clock.time = 9
        self.clock.advance(18, Action.HOUR)

        self.assertEqual(self.clock.day, Clock.TUESDAY)

    def test_advance_should_roll_day_over_multiple_day_when_time_exceeds_48_plus(self):
        """
        advance should roll day over multiple days when time exceeds 48+ hours
        """
        self.clock.day = Clock.MONDAY
        self.clock.time = 9
        self.clock.advance(2, Action.DAY)

        self.assertEqual(self.clock.day, Clock.WEDNESDAY)

    def test_advance_should_roll_back_to_start_of_week_when_day_goes_past_saturday(self):
        """
        advance should roll back to start of week when day goes past Saturday
        """
        self.clock.day = Clock.SATURDAY
        self.clock.time = 9
        self.clock.advance(18, Action.HOUR)

        self.assertEqual(self.clock.day, Clock.SUNDAY)

    def test_advance_should_result_in_decimals_when_not_an_even_hour(self):
        """
        advance should result in decimals when not an even hour
        """
        self.clock.time = 9
        self.clock.advance(30, Action.MIN)

        self.assertEqual(self.clock.time, 9.5)

    def test_advance_should_add_two_decimals_up_to_an_even_hour(self):
        """
        should add two decimals up to an even hour
        """
        self.clock.time = 9.5
        self.clock.advance(30, Action.MIN)

        self.assertEqual(self.clock.time, 10)

    def test_get_time_display_should_show_pm_if_time_is_after_12(self):
        """
        get_time_display should show pm if time is after 12
        """
        self.clock.time = 13

        self.assertEqual(self.clock.get_time_display(), '1:00pm')

    def test_get_time_display_should_show_am_if_time_is_before_12(self):
        """
        get_time_display should show am if time is before 12
        """
        self.clock.time = 9

        self.assertEqual(self.clock.get_time_display(), '9:00am')

    def test_get_time_display_should_show_12am_if_time_is_0(self):
        """
        get_time_display should show 12am if time is 0
        """
        self.clock.time = 0

        self.assertEqual(self.clock.get_time_display(), '12:00am')

    def test_get_time_display_should_show_12pm_if_time_is_12(self):
        """
        get_time_display should show 12pm if time is 12
        """
        self.clock.time = 12

        self.assertEqual(self.clock.get_time_display(), '12:00pm')

    def test_get_time_display_should_show_1230am_if_time_is_0_5(self):
        """
        get_time_display should show 12:30 am if time is 0.5
        """
        self.clock.time = 0.5

        self.assertEqual(self.clock.get_time_display(), '12:30am')

    def test_get_time_display_should_show_1230pm_if_time_is_12_5(self):
        """
        get_time_display should show 12:30 pm if time is 12.5
        """
        self.clock.time = 12.5

        self.assertEqual(self.clock.get_time_display(), '12:30pm')

    def test_clock_should_error_if_time_is_set_to_less_than_0(self):
        """
        should error if time is less than 0
        """

        with self.assertRaises(ValidationError):
            self.clock.time = -1
            self.clock.save()

    def test_clock_should_error_if_time_is_set_to_greater_than_24(self):
        """
        should error if time is greater than 24
        """

        with self.assertRaises(ValidationError):
            self.clock.time = 24.5
            self.clock.save()


class ExecuteActionsTests(TestCase):
    def test_each_action_type_calls_correct_execute_action_method(self):
        """
        Each action type calls the correct execute_action method
        """
        ae = ActionExecutor()
        situation = MagicMock(spec=Situation)

        IMPLEMENTED_EXECUTIONS = [
            (Action.TRA, 'Travel')
        ]

        for action_type, display_type in Action.ACTION_TYPES:
            with self.subTest(action_type=action_type, display_type=display_type):
                is_implemented = (action_type, display_type) in IMPLEMENTED_EXECUTIONS
                print(action_type, display_type)
                action = Action(action_type=action_type)
                ex = f'execute_{display_type.lower()}_action'

                self.assertTrue(hasattr(ae, ex))
                self.assertTrue(callable(getattr(ae, ex)))

                with patch.object(ae, ex) as mock:
                    ae.execute(action, situation)
                    mock.assert_called_with(action, situation)

                if not is_implemented:
                    with self.assertRaises(NotImplementedError):
                        ae.execute(action, situation)

    def test_throw_error_if_passed_non_action(self):
        """
        Throw error if passed non-action
        """
        ae = ActionExecutor()
        situation = MagicMock(spec=Situation)

        with self.assertRaises(TypeError):
            ae.execute('not an action', situation)

    def test_throw_error_if_passed_non_situation(self):
        """
        Throw error if passed non-situation
        """
        ae = ActionExecutor()
        action = MagicMock(spec=Action)

        with self.assertRaises(TypeError):
            ae.execute(action, 'not a situation')








