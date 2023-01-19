from django.test import TestCase

from .models import Item

from .game_logic import gen_shopping_actions


# Create your tests here.

class GenShoppingActionsTests(TestCase):
    def test_returns_list(self):
        """
        Returns a list
        """
        contents = Item.objects.all()[:0]
        inventory = Item.objects.all()[:0]
        actions = gen_shopping_actions(contents, inventory)
        self.assertIsInstance(actions, list)
