from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from comunication.models import Read
from accounts.models import Profile, Company

from django.db.models.functions import TruncDate
from .forms import RegisterForm

from django.contrib.auth.decorators import login_required #view funcionario


def login_user(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('Carma')   # deixa a view Carma() montar o contexto certo

        else:
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos'})

    return render(request, 'login.html')