from django.urls import path
from .views import login_user
from accounts import views
from django.urls import reverse

urlpatterns = [
    path('login_user', views.login_user, name='login_user'),
]