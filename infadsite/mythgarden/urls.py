from django.urls import path

from . import views

app_name = 'mythgarden'
urlpatterns = [
    path('', views.home, name='home'),
]
