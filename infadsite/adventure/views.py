from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django import forms

from .models import Quandary, Answer, Hero


def home(request):
    template_name = 'adventure/home.html'
    return render(request, template_name)

def theEnd(request, hero_id):
    try:
        hero = Hero.objects.get(pk=hero_id)
    except (KeyError, Hero.DoesNotExist):
        hero = None

    context = {
        'hero': hero
    }
    template_name = 'adventure/the-end.html'
    return render(request, template_name, context)

# class QuandaryForm(forms.Form):
#     answer = forms.ModelChoiceField(queryset=Answer.objects.all())


class QuandaryView(generic.DetailView):
    model = Quandary
    template_name = 'adventure/quandary.html'


class JourneyView(generic.DetailView):
    model = Hero
    template_name = 'adventure/journey.html'


ANSWER_FORM_PREFIX = 'answer_'

def choose(request, quandary_id):
    quandary = get_object_or_404(Quandary, pk=quandary_id)
    try:
        answers = [key for key, value in request.POST.items() if key.startswith(ANSWER_FORM_PREFIX)]
        if len(answers) == 0:
            raise KeyError
        if len(answers) == 1:
            answer_id = answers[0].replace(ANSWER_FORM_PREFIX, '')
            selected_answer = quandary.answers.get(pk=answer_id)
    except (KeyError, Answer.DoesNotExist):
        # Redisplay the quandary form.
        return render(request, 'adventure/quandary.html', {
            'quandary': quandary,
            'error_message': "Oops, didn't get a proper answer on our end.",
        })
    else:
        if selected_answer.child_quandary:
            return HttpResponseRedirect(reverse('adventure:quandary', args=(selected_answer.child_quandary.id,)))
        else:
            hero = Hero.objects.create(moniker=selected_answer.answer_text)
            return HttpResponseRedirect(reverse('adventure:the-end', args=(hero.id,)))
