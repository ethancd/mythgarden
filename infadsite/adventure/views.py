from django.http import Http404

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Quandary

# Create your views here.

def index(request):
    first_quandaries_list = Quandary.objects.order_by('created_at')[:5]
    context = {
        'first_quandaries_list': first_quandaries_list,
    }
    return render(request, 'adventure/index.html', context)

def quandary_card(request, quandary_id):
    quandary = get_object_or_404(Quandary, pk=quandary_id)
    return render(request, 'adventure/quandary_card.html', {'quandary': quandary})

