from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path('author/', views.IMommyHere.as_view(), name='author'),
    path('tech/', views.Tech.as_view(), name='tech')
]
