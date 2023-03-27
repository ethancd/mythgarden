from sqlite3 import IntegrityError
import json

from django.core.validators import ValidationError
from django.db import transaction
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from .view_helpers import load_session, get_home_models, get_requested_action, get_serialized_messages, \
    validate_action, custom_serialize, set_user_data
from .game_logic import ActionGenerator, ActionExecutor, EventOperator
from .models import Session


@ensure_csrf_cookie
def home(request):
    session = load_session(request)
    home_models = get_home_models(session)

    context = {'ctx': {model_name: custom_serialize(data) for model_name, data in home_models.items()}}

    template_name = 'mythgarden/home.html'
    return render(request, template_name, context)


def action(request):
    """Modifies game state data based on the requested action and returns a JsonResponse containing new game state data,
    or returns an error message if the action is not available."""
    if not request.method == 'POST':
        return HttpResponseRedirect(reverse('mythgarden:home'))

    session = get_object_or_404(Session, pk=request.session['session_key'])

    try:
        requested_action = get_requested_action(request, session)
        validate_action(session, requested_action)
        with transaction.atomic():
            updated_models = ActionExecutor().execute(requested_action, session)
            updated_models['actions'] = ActionGenerator().get_actions_for_session(session)
    except (ValidationError, IntegrityError) as e:
        session.messages.create(text=e.message, is_error=True)
        return JsonResponse({'error': e.message, 'messages': get_serialized_messages(session)})

    if session.game_over:
        with transaction.atomic():
            EventOperator().trigger_game_over(session)
        return JsonResponse({'gameOver': True})
    else:
        results = {model_name: custom_serialize(data) for model_name, data in updated_models.items()}
        return JsonResponse(results)


def kys(request):
    """A shortcut to reset the game state to the start of the week. A staple for timeloop games everywhere."""
    session = get_object_or_404(Session, pk=request.session['session_key'])

    EventOperator().trigger_kys(session)
    return HttpResponseRedirect(reverse('mythgarden:home'))


def user_data(request):
    """Endpoint for updating user data like hero's name, choice of portrait, etc."""
    if not request.method == 'POST':
        return HttpResponseRedirect(reverse('mythgarden:home'))

    session = get_object_or_404(Session, pk=request.session['session_key'])

    try:
        hero = session.hero
        new_data = json.loads(request.body)['userData']
        print(new_data)
        with transaction.atomic():
            success_message = set_user_data(hero, new_data)
            if success_message:
                session.messages.create(text=success_message)
    except ValidationError as e:
        session.messages.create(text=e.message, is_error=True)
        return JsonResponse({'error': e.message, 'messages': get_serialized_messages(session)})

    return JsonResponse({'messages': get_serialized_messages(session)})
