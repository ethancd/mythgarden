from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse

from .game_logic import ActionGenerator, ActionExecutor
from .static_helpers import srs_serialize
import json

from .models import Session


@ensure_csrf_cookie
def home(request):
    session = Session.objects.find_or_create(pk=request.session['session_key'])
    actions = get_current_actions(session)

    context = {
        'hero': session.hero,
        'clock': session.clock,
        'wallet': session.wallet,
        'place': session.location,
        'inventory': session.inventory.items.all(),
        'actions': actions,
        'buildings': session.location.buildings.all(),
        'contents': session.place_contents.all(),
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
        ?buildings: [{
            name: string,
            image: {
                url: string
            },
        }],
        ?contents: [{
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

        session = Session.objects.get_object_or_404(pk=request.session['session_key'])
        actions = get_current_actions(session)

        print(f'looking for {description} in {actions}')
        matches = [a for a in actions if a.description == description]

        if len(matches) == 1:
            requested_action = matches[0]
        elif len(matches) > 1:
            return JsonResponse({'error': f'Multiple actions match description: {description}'})
        else:  # len(matches) == 0
            return JsonResponse({'error': 'requested action not available'})

        if not can_pay_cost(session.wallet, requested_action):
            return JsonResponse({'error': 'hero cannot afford requested action'})

        updated_models = ActionExecutor().execute(requested_action, session)
        updated_models['actions'] = get_current_actions(session)

        results = {k: srs_serialize(v) for k, v in updated_models.items()}
        results['log_statement'] = requested_action.log_statement

        return JsonResponse(results)
    else:
        return HttpResponseRedirect(reverse('mythgarden:home'))


def get_current_actions(session):
    inventory = list(session.inventory.items.all())
    place = session.location
    contents = list(session.location.session_data.contents.all())
    villagers = list(session.location.session_data.occupants.all())

    actions = ActionGenerator().gen_available_actions(place, inventory, contents, villagers)

    return actions


def can_pay_cost(wallet, requested_action):
    if requested_action.is_cost_in_money:
        return wallet.money >= requested_action.cost_amount
    else:
        return True

