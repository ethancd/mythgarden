from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Quandary, Answer, Hero


class IndexView(generic.ListView):
    template_name = 'adventure/index.html'
    context_object_name = 'first_quandaries_list'

    def get_queryset(self):
        """Return the first five published quandaries that have any answers."""
        quandaries = Quandary.objects.filter(answers__isnull=False).distinct()

        return quandaries.order_by('created_at')[:5]


class QuandaryCardView(generic.DetailView):
    model = Quandary
    template_name = 'adventure/quandary_card.html'


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