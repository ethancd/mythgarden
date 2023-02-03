from django.test import TestCase
from unittest.mock import MagicMock, patch
from django.core.validators import ValidationError
from itertools import count
from sqlite3 import IntegrityError

from .models import Item, Action, Villager, Place, Bridge, Building, Hero, Clock, Session

from .game_logic import ActionGenerator, ActionExecutor


def assertAnyActionsOfType(actions, action_type):
    """Asserts that at least one action in the list of actions is of the given type"""
    for action in actions:
        if action.action_type == action_type:
            return
    raise AssertionError(f"No actions of type {action_type} found in {actions}")


def create_item(name=None, item_type=Item.GIFT, price=1, rarity=Item.COMMON, counter=count()):
    if name is None:
        name = f'Mock Item #{next(counter)}'

    try:
        return Item.objects.create(name=name, item_type=item_type, price=price, rarity=rarity)
    except IntegrityError:
        print(f'Item with name {name} already exists. Oops!')


def create_villager(name='Lea', home=None):
    return Villager.objects.create(name=name, home=home)


def create_place(name='Nowheresville', place_type=Place.TOWN):
    return Place.objects.create(name=name, place_type=place_type)


def create_bridge(place_1, place_2, direction_1=Bridge.WEST, direction_2=Bridge.EAST):
    return Bridge.objects.create(place_1=place_1, place_2=place_2, direction_1=direction_1, direction_2=direction_2)


def create_building(name, place, place_type):
    return Building.objects.create(name=name, surround=place, place_type=place_type)


def create_hero(name='Stan'):
    return Hero.objects.create(name=name)


def create_session(skip_post_save_signal=True):
    return Session.objects.create(skip_post_save_signal=skip_post_save_signal)


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

        self.ag.gen_gather_actions = MagicMock()
        self.gather_actions = ['gather']
        self.ag.gen_gather_actions.return_value = self.gather_actions

        self.ag.gen_enter_actions = MagicMock()
        self.enter_actions = ['enter']
        self.ag.gen_enter_actions.return_value = self.enter_actions

        self.ag.gen_exit_action = MagicMock()
        self.exit_action = ['exit']
        self.ag.gen_exit_action.return_value = self.exit_action

        self.town = create_place('The Town', Place.TOWN)
        self.farm = create_place('The Farm', Place.FARM)
        self.mountains = create_place('The Mountains', Place.MOUNTAIN)
        self.beach = create_place('The Beach', Place.BEACH)
        self.forest = create_place('The Forest', Place.FOREST)
        self.inventory = []
        self.contents = []
        self.villagers = []

    def test_returns_list(self):
        """Returns a list"""
        actions = self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        self.assertIsInstance(actions, list)

    def test_calls_gen_farming_actions_when_place_type_is_farm(self):
        """Calls gen_farming_actions when place_type is farm"""
        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_farming_actions.assert_called_once_with(self.contents, self.inventory)

    def test_returns_farming_actions_when_place_type_is_farm(self):
        """Returns farming actions when place_type is farm"""
        actions = self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.assertEqual(actions, self.farming_actions)

    def test_does_not_call_gen_farming_actions_when_place_is_not_place_type_farm(self):
        """Does not call gen_farming_actions when place_type is not farm"""
        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        self.ag.gen_farming_actions.assert_not_called()

    def test_calls_gen_shopping_actions_when_place_is_a_shop_building(self):
        """Calls gen_shopping_actions when place is a building with place_type shop"""
        self.shop = create_building('Shop', self.town, Place.SHOP)

        self.ag.gen_available_actions(self.shop, self.inventory, self.contents, self.villagers)

        self.ag.gen_shopping_actions.assert_called_once_with(self.contents, self.inventory)

    def test_returns_shopping_actions_when_place_is_a_shop_building(self):
        """Returns shopping actions when place has a shop landmark"""
        self.shop = create_building('Shop', self.town, Place.SHOP)

        actions = self.ag.gen_available_actions(self.shop, self.inventory, self.contents, self.villagers)

        for a in self.shopping_actions:
            self.assertIn(a, actions)

    def test_does_not_call_gen_shopping_actions_when_place_is_not_a_building(self):
        """Does not call gen_shopping_actions when place is not a building"""
        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        self.ag.gen_shopping_actions.assert_not_called()

    def test_does_not_call_gen_shopping_actions_when_place_is_a_building_but_not_shop(self):
        """Does not call gen_shopping_actions when place is a building but not a shop"""
        self.neighbor_house = create_building('Neighbor House', self.town, Place.HOME)

        self.ag.gen_available_actions(self.neighbor_house, self.inventory, self.contents, self.villagers)

        self.ag.gen_shopping_actions.assert_not_called()

    def test_calls_gen_travel_actions_when_place_is_place_1_of_a_saved_bridge(self):
        """Calls gen_travel_actions when place is place_1 of a bridge"""
        bridges = [create_bridge(self.town, self.forest)]

        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        self.ag.gen_travel_actions.assert_called_once_with(self.town, bridges)

    def test_returns_travel_actions_when_place_is_place_1_of_a_saved_bridge(self):
        """Returns travel actions when place is place_1 of a bridge"""
        create_bridge(self.town, self.forest)

        actions = self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        for a in self.travel_actions:
            self.assertIn(a, actions)

    def test_calls_gen_travel_actions_when_place_is_place_2_of_a_saved_bridge(self):
        """Calls gen_travel_actions when place is place_2 of a bridge"""
        bridges = [create_bridge(self.forest, self.town)]

        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        self.ag.gen_travel_actions.assert_called_once_with(self.town, bridges)

    def test_calls_gen_travel_actions_when_place_is_part_of_multiple_bridges(self):
        """Calls gen_travel_actions when place is part of multiple bridges"""
        bridges = [
            create_bridge(self.town, self.forest),
            create_bridge(self.mountains, self.town)
        ]

        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        self.ag.gen_travel_actions.assert_called_once_with(self.town, bridges)

    def test_does_not_call_gen_travel_actions_when_place_is_not_in_a_saved_bridge(self):
        """Does not call gen_travel_actions when place is not a bridge"""
        create_bridge(self.forest, self.mountains)

        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        self.ag.gen_travel_actions.assert_not_called()

    def test_calls_gen_social_actions_when_villagers_are_present(self):
        """Calls gen_social_actions when villagers are present"""
        self.villagers = [create_villager()]

        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        self.ag.gen_social_actions.assert_called_once_with(self.villagers, self.inventory)

    def test_returns_social_actions_when_villagers_are_present(self):
        """Returns social actions when villagers are present"""
        self.villagers = [create_villager()]

        actions = self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        for a in self.social_actions:
            self.assertIn(a, actions)

    def test_does_not_call_gen_social_actions_when_no_villagers_are_present(self):
        """Does not call gen_social_actions when no villagers are present"""
        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)

        self.ag.gen_social_actions.assert_not_called()

    def test_calls_gen_gather_actions_when_place_is_a_wild_type(self):
        """Calls gen_gather_actions when place is a wild type (in Place.WILD_TYPES)"""

        for place in [self.beach, self.forest, self.mountains]:
            with self.subTest(place=place):
                self.ag.gen_gather_actions = MagicMock()  # reset mock in each subtest
                self.ag.gen_available_actions(place, self.inventory, self.contents, self.villagers)
                self.ag.gen_gather_actions.assert_called_once_with(place)

    def test_returns_gather_actions_when_place_is_a_wild_type(self):
        """Returns gather actions when place is a wild type (in Place.WILD_TYPES)"""
        for place in [self.beach, self.forest, self.mountains]:
            with self.subTest(place=place):
                actions = self.ag.gen_available_actions(place, self.inventory, self.contents, self.villagers)
                for a in self.gather_actions:
                    self.assertIn(a, actions)

    def test_does_not_call_gen_gather_actions_when_place_is_not_a_wild_type(self):
        """Does not call gen_gather_actions when place is not a wild type (not in Place.WILD_TYPES)"""
        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)
        self.ag.gen_gather_actions.assert_not_called()

    def test_calls_gen_enter_actions_when_place_has_buildings(self):
        """Calls gen_enter_actions when place has buildings"""
        pub_building = create_building('the pub', self.town, Place.SHOP)

        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)
        self.ag.gen_enter_actions.assert_called_once_with([pub_building])

    def test_returns_enter_actions_when_place_has_buildings(self):
        """Returns enter actions when place has buildings"""
        create_building('the pub', self.town, Place.SHOP)

        actions = self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)
        for a in self.enter_actions:
            self.assertIn(a, actions)

    def test_does_not_call_gen_enter_actions_when_place_has_no_buildings(self):
        """Does not call gen_enter_actions when place has no buildings"""
        self.ag.gen_available_actions(self.town, self.inventory, self.contents, self.villagers)
        self.ag.gen_enter_actions.assert_not_called()

    def test_calls_gen_exit_action_when_place_is_a_building(self):
        """Calls gen_exit_action when place is a building"""
        pub_building = create_building('the pub', self.town, Place.SHOP)

        self.ag.gen_available_actions(pub_building, self.inventory, self.contents, self.villagers)
        self.ag.gen_exit_action.assert_called_once_with(pub_building, self.town)

    def test_returns_exit_action_when_place_is_a_building(self):
        """Returns exit action when place is a building"""
        pub_building = create_building('the pub', self.town, Place.SHOP)

        actions = self.ag.gen_available_actions(pub_building, self.inventory, self.contents, self.villagers)
        self.assertIn(self.exit_action, actions)

    def test_does_not_call_gen_exit_action_when_place_is_not_a_building(self):
        """Does not call gen_exit_action when place is not a building"""
        self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)
        self.ag.gen_exit_action.assert_not_called()


    def test_returns_multiple_types_of_actions_when_multiple_types_are_available(self):
        """Returns multiple types of actions when multiple types are available"""
        create_bridge(self.farm, self.forest)
        self.villagers = [create_villager()]

        actions = self.ag.gen_available_actions(self.farm, self.inventory, self.contents, self.villagers)

        for lst in [self.farming_actions, self.travel_actions, self.social_actions]:
            for a in lst:
                self.assertIn(a, actions)


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

        self.assertEqual(actions[0].log_statement, 'You bought Rock for 5 koin.')

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

        self.assertEqual(actions[0].log_statement, 'You sold Rock for 5 koin.')

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

        self.assertEqual(actions[0].cost_amount, 30)

    def test_returns_talk_actions_with_correct_cost_unit(self):
        """
        Returns a list with talk actions with the correct cost_unit
        """
        self.villagers = [create_villager()]
        actions = self.ag.gen_social_actions(self.villagers, self.inventory)

        self.assertEqual(actions[0].cost_unit, Action.MIN)

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

        self.assertEqual(gift_action.log_statement, 'You gave {item_name} to {villager_name}. Looks like they {valence_text}')

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

        self.assertEqual(gift_action.cost_amount, 5)

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

        self.assertEqual(water_action.cost_amount, 60)

    def test_returns_water_actions_with_correct_cost_unit(self):
        """
        Returns a list with water actions with the correct cost_unit
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.SPROUT)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        water_action = [a for a in actions if a.action_type == Action.WAT][0]

        self.assertEqual(water_action.cost_unit, Action.MIN)

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

        self.assertEqual(harvest_action.cost_amount, 60)

    def test_returns_harvest_actions_with_correct_cost_unit(self):
        """
        Returns a list with harvest actions with the correct cost_unit
        """
        self.field_contents = [create_item(name='Parsnip', item_type=Item.CROP)]
        actions = self.ag.gen_farming_actions(self.field_contents, self.inventory)

        harvest_action = [a for a in actions if a.action_type == Action.HAR][0]

        self.assertEqual(harvest_action.cost_unit, Action.MIN)

    def test_returns_plant_and_water_actions_when_there_are_seeds_and_sprouts(self):
        """
        Returns plant and water actions when there are seeds and sprouts
        """
        self.field_contents = [
            create_item(name='Parsnip Sprout', item_type=Item.SPROUT),
            create_item(name='Strawberry Sprout', item_type=Item.SPROUT),
        ]
        self.inventory = [
            create_item(name='Parsnip Seed', item_type=Item.SEED),
            create_item(name='Strawberry Seed', item_type=Item.SEED),
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
            create_item(name='Parsnip Crop', item_type=Item.CROP),
            create_item(name='Strawberry Crop', item_type=Item.CROP),
        ]
        self.inventory = [
            create_item(name='Parsnip Seed', item_type=Item.SEED),
            create_item(name='Strawberry Seed', item_type=Item.SEED),
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
            create_item(name='Parsnip Sprout', item_type=Item.SPROUT),
            create_item(name='Strawberry Crop', item_type=Item.CROP),
        ]
        self.inventory = [
            create_item(name='Parsnip Seed', item_type=Item.SEED),
            create_item(name='Strawberry Seed', item_type=Item.SEED),
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

        self.assertEqual(actions[0].cost_amount, 60)

    def test_returns_travel_actions_with_correct_cost_unit(self):
        """
        Returns travel actions with the correct cost unit
        """
        self.bridges = [create_bridge(self.farm, self.store)]
        actions = self.ag.gen_travel_actions(self.farm, self.bridges)

        self.assertEqual(actions[0].cost_unit, Action.MIN)

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


class GenGatherActionsTests(TestCase):
    def setUp(self):
        self.ag = ActionGenerator()
        self.mountains = create_place('Mountains', Place.MOUNTAIN)
        self.forest = create_place('Forest', Place.FOREST)
        self.beach = create_place('Beach', Place.BEACH)

    def test_returns_list(self):
        """
        Returns a list
        """
        actions = self.ag.gen_gather_actions(self.mountains)

        self.assertIsInstance(actions, list)

    def test_returns_action_of_gather_type_for_mountains(self):
        """
        Returns an action of gather type for mountains
        """
        actions = self.ag.gen_gather_actions(self.mountains)

        self.assertEqual(actions[0].action_type, Action.GAT)

    @patch('mythgarden.game_logic.ActionGenerator.gen_digging_action')
    def test_calls_gen_digging_action_for_mountains(self, mock_gen_digging_action):
        """
        Calls gen_digging_action for mountains
        """
        self.ag.gen_gather_actions(self.mountains)

        mock_gen_digging_action.assert_called()

    def test_returns_action_with_correct_description_for_mountains(self):
        """
        Returns an action with the correct description for mountains
        """
        actions = self.ag.gen_gather_actions(self.mountains)

        self.assertEqual(actions[0].description, 'Dig for something interesting')

    def test_returns_action_with_correct_log_statement_for_mountains(self):
        """
        Returns an action with the correct log statement for mountains
        """
        actions = self.ag.gen_gather_actions(self.mountains)

        self.assertEqual(actions[0].log_statement, 'You dug up a {result}!')

    def test_returns_action_of_gather_type_for_forest(self):
        """
        Returns an action of gather type for forest
        """
        actions = self.ag.gen_gather_actions(self.forest)

        self.assertEqual(actions[0].action_type, Action.GAT)

    @patch('mythgarden.game_logic.ActionGenerator.gen_foraging_action')
    def test_calls_gen_foraging_action_for_forest(self, mock_gen_foraging_action):
        """
        Calls gen_foraging_action for forest
        """
        self.ag.gen_gather_actions(self.forest)

        mock_gen_foraging_action.assert_called()

    def test_returns_action_with_correct_description_for_forest(self):
        """
        Returns an action with the correct description for forest
        """
        actions = self.ag.gen_gather_actions(self.forest)

        self.assertEqual(actions[0].description, 'Forage for plants')

    def test_returns_action_with_correct_log_statement_for_forest(self):
        """
        Returns an action with the correct log statement for forest
        """
        actions = self.ag.gen_gather_actions(self.forest)

        self.assertEqual(actions[0].log_statement, 'You found {result}!')

    def test_returns_action_of_gather_type_for_beach(self):
        """
        Returns an action of gather type for beach
        """
        actions = self.ag.gen_gather_actions(self.beach)

        self.assertEqual(actions[0].action_type, Action.GAT)

    @patch('mythgarden.game_logic.ActionGenerator.gen_fishing_action')
    def test_calls_gen_fishing_action_for_beach(self, mock_gen_fishing_action):
        """
        Calls gen_fishing_action for beach
        """
        self.ag.gen_gather_actions(self.beach)

        mock_gen_fishing_action.assert_called()

    def test_returns_action_with_correct_description_for_beach(self):
        """
        Returns an action with the correct description for beach
        """
        actions = self.ag.gen_gather_actions(self.beach)

        self.assertEqual(actions[0].description, 'Go fishing')

    def test_returns_action_with_correct_log_statement_for_beach(self):
        """
        Returns an action with the correct log statement for beach
        """
        actions = self.ag.gen_gather_actions(self.beach)

        self.assertEqual(actions[0].log_statement, 'You caught a {result}!')


class ActionModelTests(TestCase):
    def test_computes_correct_display_cost_for_time_actions(self):
        """
        Computes the correct display cost for time actions
        """
        action = Action(action_type=Action.WAT, cost_amount=1, cost_unit=Action.HOUR)

        self.assertEqual(action.display_cost, '1 hr')

    def test_computes_correct_display_cost_for_money_actions(self):
        """
        Computes the correct display cost for money actions
        """
        action = Action(action_type=Action.BUY, cost_amount=5, cost_unit=Action.KOIN)

        self.assertEqual(action.display_cost, '⚜️5')


class ClockModelTests(TestCase):
    def setUp(self):
        session = create_session()
        self.clock = Clock(session=session, day=Clock.MONDAY, time=9*60)

    def test_advance_should_advance_the_time_by_the_amount_of_hours(self):
        """
        advance should advance the time by the amount of hours
        """
        self.clock.time = 9*60
        self.clock.advance(60)

        self.assertEqual(self.clock.time, 10*60)

    def test_advance_should_roll_time_over_when_time_equals_24(self):
        """
        advance should roll time over when time equals 24*60
        """
        self.clock.time = 9*60
        self.clock.advance(15*60)

        self.assertEqual(self.clock.time, 0)

    def test_advance_should_roll_time_over_when_time_exceeds_24(self):
        """
        advance should roll time over when time exceeds 24*60
        """
        self.clock.time = 9*60
        self.clock.advance(18*60)

        self.assertEqual(self.clock.time, 3*60)

    def test_advance_should_roll_day_over_when_time_exceeds_24(self):
        """
        advance should roll day over when time exceeds 24*60
        """
        self.clock.day = Clock.MONDAY
        self.clock.time = 9*60
        self.clock.advance(18*60)

        self.assertEqual(self.clock.day, Clock.TUESDAY)

    def test_advance_should_roll_day_over_multiple_day_when_time_exceeds_48_plus(self):
        """
        advance should roll day over multiple days when time exceeds 48+ hours
        """
        self.clock.day = Clock.MONDAY
        self.clock.time = 9*60
        self.clock.advance(2*60*24)

        self.assertEqual(self.clock.day, Clock.WEDNESDAY)

    def test_advance_should_roll_back_to_start_of_week_when_day_goes_past_saturday(self):
        """
        advance should roll back to start of week when day goes past Saturday
        """
        self.clock.day = Clock.SATURDAY
        self.clock.time = 9*60
        self.clock.advance(18*60)

        self.assertEqual(self.clock.day, Clock.SUNDAY)


    def test_get_time_display_should_show_pm_if_time_is_after_12(self):
        """
        get_time_display should show pm if time is after 12
        """
        self.clock.time = 13*60

        self.assertEqual(self.clock.get_time_display(), '1:00pm')

    def test_get_time_display_should_show_am_if_time_is_before_12(self):
        """
        get_time_display should show am if time is before 12
        """
        self.clock.time = 9*60

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
        self.clock.time = 12*60

        self.assertEqual(self.clock.get_time_display(), '12:00pm')

    def test_get_time_display_should_show_1230am_if_time_is_0_5(self):
        """
        get_time_display should show 12:30 am if time is 0.5
        """
        self.clock.time = 30

        self.assertEqual(self.clock.get_time_display(), '12:30am')

    def test_get_time_display_should_show_1230pm_if_time_is_12_5(self):
        """
        get_time_display should show 12:30 pm if time is 12.5
        """
        self.clock.time = 12*60 + 30

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
        should error if time is greater than 24*60
        """

        with self.assertRaises(ValidationError):
            self.clock.time = 24*60 + 1
            self.clock.save()


class ExecuteActionsTests(TestCase):
    def setUp(self) -> None:
        self.ae = ActionExecutor()
        self.session = MagicMock(spec=Session)

    def test_each_action_type_calls_correct_execute_action_method(self):
        """
        Each action type calls the correct execute_action method
        """

        for action_type, display_type in Action.ACTION_TYPES:
            with self.subTest(action_type=action_type, display_type=display_type):
                print(action_type, display_type)
                action = Action(action_type=action_type)
                ex = f'execute_{display_type.lower()}_action'

                self.assertTrue(hasattr(self.ae, ex))
                self.assertTrue(callable(getattr(self.ae, ex)))

                with patch.object(self.ae, ex) as mock:
                    self.ae.execute(action, self.session)
                    mock.assert_called_with(action, self.session)


    def test_throw_error_if_passed_non_action(self):
        """
        Throw error if passed non-action
        """
        with self.assertRaises(TypeError):
            self.ae.execute('not an action', self.session)

    def test_throw_error_if_passed_non_session(self):
        """
        Throw error if passed non-session
        """
        action = MagicMock(spec=Action)

        with self.assertRaises(TypeError):
            self.ae.execute(action, 'not a session')


# for random.choices, return the first item in the list
# this will make pull_item_from_pool go through rarities deterministically:
# common -> uncommon -> rare -> epic
@patch('random.choices', side_effect=lambda c, *args, **kwargs: [c[0]])
class PullItemFromPoolTests(TestCase):
    def setUp(self) -> None:
        self.ae = ActionExecutor()
        self.session = MagicMock(spec=Session)
        self.location = create_place()

    def test_pull_item_from_pool_returns_an_item(self, mock_random_choices):
        """
        pull_item_from_pool returns an item
        """
        self.location.item_pool.set([create_item(), create_item()])

        item = self.ae.pull_item_from_pool(self.location)

        self.assertIsInstance(item, Item)

    def test_pull_returns_item_of_correct_rarity_when_only_rarity_in_pool(self, mock_random_choices):
        """
        pull_item_from_pool returns the right rarity of item when only that rarity of item is in the pool
        """

        for rarity in Item.RARITIES:
            with self.subTest(rarity=rarity):
                self.location.item_pool.set([
                    create_item(rarity=rarity),
                    create_item(rarity=rarity)
                ])

                item = self.ae.pull_item_from_pool(self.location)

                self.assertEqual(item.rarity, rarity)

    def test_pull_returns_valid_item_when_multiple_rarities_in_pool(self, mock_random_choices):
        """
        pull_item_from_pool returns a valid item when multiple rarities of item are in the pool
        we've mocked random.choices to return first item in list, so expect a common item
        """
        self.location.item_pool.set([
            create_item(rarity=Item.COMMON),
            create_item(rarity=Item.UNCOMMON),
            create_item(rarity=Item.RARE),
            create_item(rarity=Item.EPIC)
        ])

        item = self.ae.pull_item_from_pool(self.location)

        self.assertEqual(item.rarity, Item.COMMON)

    def test_pull_calls_random_choices_with_correct_weights(self, mock_random_choices):
        """
        pull_item_from_pool calls random.choices with the correct weights
        """
        self.location.item_pool.set([create_item(), create_item()])

        self.ae.pull_item_from_pool(self.location)

        mock_random_choices.assert_called_with(
            Item.RARITIES,
            weights=[v for k, v in Item.RARITY_WEIGHTS.items()],
            k=1
        )

    def test_pull_item_from_pool_raises_error_if_pool_is_empty(self, mock_random_choices):
        """
        pull_item_from_pool raises error if pool is empty
        """
        self.location.item_pool.set(Item.objects.none())

        with self.assertRaises(ValueError):
            self.ae.pull_item_from_pool(self.location)










