from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from comunication.models import Read
from accounts.models import Profile, Company

from django.db.models.functions import TruncDate
from django.db.models import DateField 
from .forms import RegisterForm

from django.contrib.auth.decorators import login_required #view funcionario

def login_user(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request, user)
            # A view Carma monta o painel correto conforme o perfil do usuário.
            return redirect('Carma')

        else:
            return render(request,'login.html',{'error': 'Usuário ou senha inválidos'})
    return render(request, 'login.html')

def cadastro(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            #Formulário
            full_name = form.cleaned_data['full_name']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            company = form.cleaned_data['company']

            #Usuário
            user = User.objects.create_user(
                username=username,
                password=password
            )

            user.first_name = full_name
            user.save()

            Profile.objects.create(user=user,company=company,role='EMPLOYEE')
            return redirect('login_user')

    else:

        form = RegisterForm()

    return render(request,'cadastro.html',{'form': form,'companies': Company.objects.all()})

