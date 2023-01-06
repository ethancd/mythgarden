from django.urls import path

from . import views

app_name = 'adventure'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.QuandaryCardView.as_view(), name='quandary_card'),
    path('journey/<int:pk>/', views.JourneyView.as_view(), name='journey'),
    path('<int:quandary_id>/choose/', views.choose, name='choose'),
]