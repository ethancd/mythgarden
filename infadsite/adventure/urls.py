from django.urls import path

from . import views

app_name = 'adventure'
urlpatterns = [
    path('', views.home, name='home'),
    path('the-end', views.theEnd, name='the-end'),
    path('the-end/<int:hero_id>', views.theEnd, name='the-end'),
    path('<int:pk>/', views.QuandaryView.as_view(), name='quandary'),
    path('journey/<int:pk>/', views.JourneyView.as_view(), name='journey'),
    path('<int:quandary_id>/choose/', views.choose, name='choose'),
]