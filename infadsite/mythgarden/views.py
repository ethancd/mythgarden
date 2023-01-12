from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django import forms

# from .models import Quandary, Answer, Hero


def home(request):
    template_name = 'mythgarden/home.html'
    return render(request, template_name)