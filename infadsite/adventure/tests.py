from django.test import TestCase
from django.urls import reverse

from .models import Quandary, Answer, Hero


class QuandaryModelTests(TestCase):
    def test_quandary_has_quandary_text(self):
        """
        Quandary has quandary_text
        """
        q = Quandary(quandary_text="What is the meaning of life?", description="")
        self.assertEqual(q.quandary_text, "What is the meaning of life?")

    def test_quandary_has_description_is_true_when_present(self):
        """
        Quandary has description
        """
        q = Quandary(quandary_text="What is the meaning of life?", description="Life is a mystery.")
        self.assertEqual(q.description, "Life is a mystery.")
        self.assertIs(q.has_description(), True)

    def test_quandary_has_description_is_false_when_empty(self):
        """
        has_description() returns False for quandaries whose
        description is empty.
        """
        q = Quandary(quandary_text="What is the meaning of life?", description="")
        self.assertIs(q.has_description(), False)

    def test_quandary_has_created_at(self):
        """
        Quandary has created_at
        """
        q = Quandary(quandary_text="What is the meaning of life?", description="")
        q.save()
        self.assertIsNotNone(q.created_at)


class AnswerModelTests(TestCase):
    def test_answer_has_answer_text(self):
        """
        Answer has answer_text
        """
        q = Quandary(quandary_text="What is the meaning of life?", description="")
        q.save()
        a = Answer(quandary=q, answer_text="42")
        self.assertEqual(a.answer_text, "42")

    def test_answer_has_created_at(self):
        """
        Answer has created_at
        """
        q = Quandary(quandary_text="What is the meaning of life?", description="")
        q.save()
        a = Answer(quandary=q, answer_text="42")
        a.save()
        self.assertIsNotNone(a.created_at)

    def test_answer_has_quandary(self):
        """
        Answer has quandary
        """
        q = Quandary(quandary_text="What is the meaning of life?", description="")
        q.save()
        a = Answer(quandary=q, answer_text="42")
        self.assertEqual(a.quandary, q)


class HeroModelTests(TestCase):
    def test_hero_has_moniker(self):
        """
        Hero has a moniker
        """
        hero = Hero(moniker="Hero Alpha")
        self.assertEqual(hero.moniker, "Hero Alpha")

    def test_hero_has_answers_given(self):
        """
        Hero has answers given
        """
        hero = Hero(moniker="Hero Alpha")
        hero.save()

        quandary = Quandary(quandary_text="What is your name?")
        quandary.save()

        answer = Answer(quandary=quandary, answer_text="My name is Hero Alpha")
        answer.save()

        hero.answers_given.set([answer])
        hero.save()

        self.assertQuerysetEqual(
            hero.answers_given.all(),
            [answer]
        )

    def test_hero_has_created_at(self):
        """
        Hero has created_at
        """
        hero = Hero(moniker="Hero Alpha")
        hero.save()
        self.assertIsNotNone(hero.created_at)

    def test_hero_has_str(self):
        """
        Hero has str
        """
        hero = Hero(moniker="Hero Alpha")
        hero.save()
        self.assertEqual(str(hero), "Hero Alpha")


def create_quandary(quandary_text, answer_count):
    """
    Create a quandary with the given `quandary_text` and `answer_count` answers.
    """
    q = Quandary.objects.create(quandary_text=quandary_text)

    for i in range(answer_count):
        Answer.objects.create(quandary_id=q.id, answer_text="Answer {}".format(i))
    return q


class QuandaryIndexViewTests(TestCase):
    def test_no_quandaries(self):
        """
        If no quandaries exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('adventure:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No quandaries are available.")
        self.assertQuerysetEqual(response.context['first_quandaries_list'], [])

    def test_quandary_with_answers(self):
        """
        Quandaries with any answers are displayed on the index page.
        """
        q_with_a = create_quandary(quandary_text="What is your name?", answer_count=3)
        response = self.client.get(reverse('adventure:index'))

        self.assertQuerysetEqual(
            response.context['first_quandaries_list'],
            [q_with_a]
        )

    def test_quandary_without_answers(self):
        """
        Quandaries without any answers aren't displayed on the index page.
        """
        response = self.client.get(reverse('adventure:index'))
        self.assertContains(response, "No quandaries are available.")
        self.assertQuerysetEqual(response.context['first_quandaries_list'], [])

    def test_quandary_with_answers_and_without_answers(self):
        """
        Even if both answerable and unanswerable quandaries are present, only quandaries with answers
        are displayed.
        """
        q_with_a = create_quandary(quandary_text="What is your name?", answer_count=3)
        create_quandary(quandary_text="What is the sound of one hand clapping?", answer_count=0)
        response = self.client.get(reverse('adventure:index'))
        self.assertQuerysetEqual(
            response.context['first_quandaries_list'],
            [q_with_a]
        )

    def test_two_quandaries_with_answers(self):
        """
        The quandaries index page may display multiple quandaries.
        """

        q1 = create_quandary(quandary_text="What is your name?", answer_count=3)
        q2 = create_quandary(quandary_text="What is your quest?", answer_count=3)
        response = self.client.get(reverse('adventure:index'))
        self.assertQuerysetEqual(
            response.context['first_quandaries_list'],
            [q1, q2]
        )
