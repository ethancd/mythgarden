from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
import json

from .models import Hero, Place


@ensure_csrf_cookie
def home(request):
    hero = Hero.objects.all()[:1].get()
    situation = hero.situation
    place = situation.place
    actions = situation.gen_available_actions()

    context = {
        'hero': hero,
        'place': place,
        'actions': actions,
    }

    template_name = 'mythgarden/home.html'
    return render(request, template_name, context)


def action(request):
    if request.method == 'POST':
        action_type = json.loads(request.body)['actionType']
        results = {}

        if is_travel(action_type):
            results['new_location'] = gen_new_location(action_type)

        if is_plant(action_type):
            results['new_crops'] = gen_new_crops(action_type)

        return JsonResponse(results)
    else:
        return HttpResponseRedirect(reverse('mythgarden:home'))


def is_travel(action_type):
    return 'walk' in action_type


def is_plant(action_type):
    return 'plant' in action_type


def gen_new_location(action_type):
    return 'General Store'


def gen_new_crops(action_type):
    return 'Parsnips'
