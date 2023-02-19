from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
from django.core.validators import ValidationError
from django.db import transaction
from sqlite3 import IntegrityError

from .game_logic import ActionGenerator, ActionExecutor, EventOperator, can_afford_action
from .static_helpers import srs_serialize
import json

from .models import Session


@ensure_csrf_cookie
def home(request):
    session_key = request.session.get('session_key', None)

    print(f'----------Session key is {session_key}-----------')

    if session_key is None:
        session = Session.objects.create()
        print(f'----------Created new session with key {session.pk}-----------')
        request.session['session_key'] = session.pk
    else:
        session = Session.objects.get_or_create(pk=session_key)[0]

    actions = get_current_actions(session)

    context = {
        'ctx': {
            'hero': session.hero,
            'clock': session.clock,
            'wallet': session.wallet,
            'message': session.message,
            'place': session.location,
            'inventory': srs_serialize(session.inventory.item_tokens.all()),
            'actions': srs_serialize(actions),
            'buildings': session.location.buildings.all(),
            'local_item_tokens': session.local_item_tokens.all(),
            'villager_states': session.occupant_states.all(),
        }
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
        ?villagers: [{
            name: string,
        }],
        ?place_contents: [{
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

        session = get_object_or_404(Session, pk=request.session['session_key'])
        actions = get_current_actions(session)

        print(f'looking for {description} in {actions}')
        matches = [a for a in actions if a.description == description]

        if len(matches) >= 1:
            requested_action = matches[0]
        else:  # len(matches) == 0
            return JsonResponse({'error': 'requested action not available'})

        if not can_afford_action(session.wallet, requested_action):
            return JsonResponse({'error': 'hero cannot afford requested action'})

        try:
            with transaction.atomic():
                updated_models, log_statement = ActionExecutor().execute(requested_action, session)
        except (ValidationError, IntegrityError) as e:
            return JsonResponse({'error': e.message})

        if session.game_over:
            EventOperator().trigger_game_over(session)
            return JsonResponse({'game_over': True})

        updated_models['actions'] = get_current_actions(session)

        results = {k: srs_serialize(v) for k, v in updated_models.items()}
        results['log_statement'] = log_statement

        return JsonResponse(results)
    else:
        return HttpResponseRedirect(reverse('mythgarden:home'))


def get_current_actions(session):
    place = session.location
    inventory = list(session.inventory.item_tokens.all())
    contents = list(session.local_item_tokens.all())
    villager_states = list(session.occupant_states.all())
    clock = session.clock

    actions = ActionGenerator().gen_available_actions(place, inventory, contents, villager_states, clock)

    return actions

