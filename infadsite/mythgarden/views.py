from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse

from .game_logic import ActionGenerator, ActionExecutor
import json

from .models import Hero


@ensure_csrf_cookie
def home(request):
    hero = Hero.objects.all()[:1].get()
    place = hero.situation.place

    actions = get_current_actions(hero)

    context = {
        'hero': hero,
        'place': place,
        'actions': actions,
    }

    template_name = 'mythgarden/home.html'
    return render(request, template_name, context)


def action(request):
    """Modifies game state data based on the requested action and returns a JsonResponse containing new game state data,
    or returns an error message if the action is not available.

    results = {
        ?clock: Clock,
        ?wallet: Wallet,
        ?place: Place,
        ?inventory: [Item],
        ?landmark_contents: [Item],
        log_statement: str,
        actions: [Action],
    }
    """
    if request.method == 'POST':
        description = json.loads(request.body)['description']

        hero = Hero.objects.all()[:1].get()
        actions = get_current_actions(hero)

        requested_action = [a for a in actions if a.description == description][0]

        if not requested_action:
            return JsonResponse({'error': 'requested action not available'})

        if not can_pay_cost(hero, requested_action):
            return JsonResponse({'error': 'hero cannot afford requested action'})

        results = ActionExecutor().execute(requested_action, hero.situation)

        results['log_statement'] = requested_action.log_statement
        results['actions'] = get_current_actions(hero)

        return JsonResponse(results)
    else:
        return HttpResponseRedirect(reverse('mythgarden:home'))


def get_current_actions(hero):
    inventory = list(hero.rucksack.contents.all())

    situation = hero.situation
    place = situation.place
    contents = list(situation.contents.all())
    villagers = list(situation.occupants.all())

    actions = ActionGenerator().gen_available_actions(place, inventory, contents, villagers)

    return actions


def can_pay_cost(hero, requested_action):
    if requested_action.is_cost_in_money:
        return hero.wallet.amount >= requested_action.cost_amount
    else:
        return True

