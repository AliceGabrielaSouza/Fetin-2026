from django.urls import path

from comunication.views import Make_Read
from . import views


urlpatterns = [
    path('Make_Read', views.Make_Read, name="Make_Read"),
    path('Make_Read/', views.Make_Read, name="Make_Read_slash"),
]
