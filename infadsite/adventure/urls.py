from django.urls import path

from . import views

app_name = 'adventure'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:quandary_id>/', views.quandary_card, name='quandary_card'),
]