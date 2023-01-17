from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
from django.views import generic
from django import forms
import json

# from .models import Quandary, Answer, Hero


@ensure_csrf_cookie
def home(request):
    template_name = 'mythgarden/home.html'
    return render(request, template_name)


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
