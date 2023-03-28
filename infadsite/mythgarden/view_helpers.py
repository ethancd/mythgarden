import json
from typing import Iterable
from django.core.validators import ValidationError

from .game_logic import ActionGenerator, can_afford_action
from .models import Session, FarmerPortrait


def load_session(request):
    """Loads a session from the database or creates a new one if one does not exist.
    Also saves the session key to the request session."""
    
    session_key = request.session.get('session_key', None)

    if session_key is None:
        session = Session.objects.create(is_first_session=True)
        request.session['session_key'] = session.pk
        return session

    try:
        session = Session.objects.get(pk=session_key)
    except Session.DoesNotExist:
        session = Session.objects.create(pk=session_key, is_first_session=True)

    return session


def get_home_models(session):
    """Returns a dictionary of models that are needed to render the home page."""
    actions = ActionGenerator().get_actions_for_session(session)
    portrait_urls = FarmerPortrait.get_gallery_portrait_urls()

    return {
        'actions': actions,
        'portraitUrls': portrait_urls,
        'hero': session.hero_state,
        'clock': session.clock,
        'wallet': session.wallet,
        'messages': session.messages.all(),
        'place': session.location,
        'inventory': session.inventory.item_tokens.all(),
        'buildings': session.location.buildings.all(),
        'localItemTokens': session.local_item_tokens.all(),
        'villagerStates': session.occupant_states.all(),
    }


def get_requested_action(request, session):
    action_digest = json.loads(request.body)['uniqueDigest']
    available_actions = ActionGenerator().get_actions_for_session(session)

    try:
        return [a for a in available_actions if a.unique_digest == action_digest][0]
    except IndexError:
        raise ValidationError('requested action not available')


def get_serialized_messages(session):
    return custom_serialize(list(session.messages.all()))


def validate_action(session, requested_action):
    if not can_afford_action(session.wallet, requested_action):
        raise ValidationError('hero cannot afford requested action')


def custom_serialize(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, Iterable):
        return [custom_serialize(i) for i in obj]
    else:
        return obj.serialize()


def set_user_data(hero, data):
    updated_fields = []

    if data.get('name') and hero.name != data['name']:
        hero.name = data['name']
        updated_fields.append('farmer name')

    if data.get('portraitPath') and hero.portrait.image_path != data['portraitPath']:
        new_portrait = FarmerPortrait.objects.get(image_path=data['portraitPath'])
        hero.portrait = new_portrait
        updated_fields.append('portrait')

    hero.save()

    if len(updated_fields) > 0:
        return f"Saved new {' & '.join(updated_fields)}!"
    else:
        return None
