from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django import forms

from .models import Quandary, Answer, Hero


def home(request):
    template_name = 'adventure/home.html'
    context = {
        'initial_quandary_id': 1,
    }
    return render(request, template_name, context)

# class QuandaryForm(forms.Form):
#     answer = forms.ModelChoiceField(queryset=Answer.objects.all())

class QuandaryCardView(generic.DetailView):
    model = Quandary
    template_name = 'adventure/quandary_card.html'

    def get_queryset(self):
        """
        Excludes any quandaries that don't have any answers.
        """
        return Quandary.objects.filter(answers__isnull=False).distinct()


class JourneyView(generic.DetailView):
    model = Hero
    template_name = 'adventure/journey.html'


def choose(request, quandary_id):
    quandary = get_object_or_404(Quandary, pk=quandary_id)
    try:
        selected_answer = quandary.answers.get(pk=request.POST['answer'])
    except (KeyError, Answer.DoesNotExist):
        # Redisplay the quandary form.
        return render(request, 'adventure/quandary_card.html', {
            'question': quandary,
            'error_message': "You didn't select an answer.",
        })
    else:
        new_hero = Hero(moniker="Hero Alpha")
        new_hero.save()

        new_hero.answers_given.set([selected_answer])
        new_hero.save()

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('adventure:journey', args=(new_hero.id,)))