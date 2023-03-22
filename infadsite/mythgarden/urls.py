from django.urls import path

from . import views

app_name = 'mythgarden'
urlpatterns = [
    path('', views.home, name='home'),
    path('action', views.action, name='action'),
    path('kys', views.kys, name='kys')
]
