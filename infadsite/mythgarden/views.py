from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder

from .game_logic import ActionGenerator, ActionExecutor
from .static_helpers import srs_serialize
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
        'landmarks': place.landmarks.all(),
        'landmark_contents': hero.situation.contents.all(),
        'inventory': hero.rucksack.contents.all(),
        'actions': actions,
    }

    template_name = 'mythgarden/home.html'
    return render(request, template_name, context)


def action(request):
    """Modifies game state data based on the requested action and returns a JsonResponse containing new game state data,
    or returns an error message if the action is not available.

    results = {
        ?clock: string,
        ?wallet: string,
        ?place: {
            name: string,
            image: {
                url: string
            },
        },
        ?inventory: [{
            name: string,
        }],
        ?landmarks: [{
            name: string,
            is_field_or_shop: bool,
        }],
        ?landmark_contents: [{
            name: string,
        }],
        log_statement: str,
        actions: [{
            description: string,
            display_cost: string,
        }]
    }
    """
    if request.method == 'POST':
        description = json.loads(request.body)['description']

        hero = Hero.objects.all()[:1].get()
        actions = get_current_actions(hero)

        print(f'looking for {description} in {actions}')

        matches = [a for a in actions if a.description == description]

        if len(matches) == 1:
            requested_action = matches[0]
        elif len(matches) > 1:
            raise Exception(f'Multiple actions match description: {description}')
        else:  # len(matches) == 0
            return JsonResponse({'error': 'requested action not available'})

        if not can_pay_cost(hero, requested_action):
            return JsonResponse({'error': 'hero cannot afford requested action'})

        updated_models = ActionExecutor().execute(requested_action, hero.situation)
        updated_models['actions'] = get_current_actions(hero)

        results = {}
        for k, v in updated_models.items():
            print(f'{k}: {v}')
            results[k] = srs_serialize(v)

        # results = {k: serialize("json", v) for k, v in updated_models.items()}
        results['log_statement'] = requested_action.log_statement

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
        return hero.wallet.money >= requested_action.cost_amount
    else:
        return True

