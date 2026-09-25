from datetime import date, datetime
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.utils import timezone
from django.db.models.functions import TruncDate

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

from accounts.models import Company, Profile
from accounts.forms import RegisterForm

from comunication.models import Read, Car, CarAssignment
from comunication.forms import CarAssignmentForm

def index(request):
    return render(request, 'index.html', {'titulo': 'Bem Vindos!'})

def History(request):
    return render(request, 'History.html', {'titulo1': 'História do Projeto'})

def ONU(request):
    return render(request, 'ONU.html', {'titulo2': 'Impacto na Sociedade'})

def Contact(request):
    return render(request, 'Contact.html', {'titulo3': 'Equipe'})

def Login(request):
    return render(request, 'Login.html', {'titulo2': 'Impacto na Sociedade'})

def Information(request, date):
    # Converta a string da data recebida da URL em um objeto de data
    selected_date = datetime.strptime(date, '%Y-%m-%d').date()

    # Filtra as leituras do usuário autenticado com base na data
    user_reads = Read.objects.filter(client=request.user, timestamp__date=selected_date)
    
    for read in user_reads:
        read.timestamp = read.timestamp.strftime("%H:%M:%S")  # Formata apenas o horário
    # Renderiza o template 'Information.html' com os dados filtrados
    return render(request, 'Information.html', {
        'selected_date': selected_date,
        'user_reads': user_reads,
    })

def read_by_date(request, date):
    # Filtra as leituras pela data fornecida
    user_reads = Read.objects.filter(timestamp__date=date, client=request.user)

    return render(request, 'Information.html', {'user_reads': user_reads, 'selected_date': date})

def save_txt(request,date):
     if request.method == 'GET':
        # Obter o dia atual
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        # Buscar todas as leituras do dia atual no banco de dados
        day = Read.objects.filter(client=request.user, timestamp__date=date)

        # Verificação se há dados para salvar
        if not day.exists():
            return HttpResponse("Nenhuma leitura encontrada para o dia de hoje.")


        # Usar StringIO para armazenar o conteúdo antes de criar o arquivo
        file_content = io.StringIO()

        # Adicionar as informações ao arquivo
        for read in day:
            line = ""
            if read.speed == 1:
                line += f"Velocidade: {read.speed} km/h, "

            if read.braking == 1:
                line += f"Freio ativado "

            if read.turn_signal != 0 :
                line += "Seta Ligada"
            
            if line:
                # Adicionar o timestamp à linha e escrever no arquivo
                line += f"  Timestamp: {read.timestamp}\n"
                file_content.write(line)
        # Definir o conteúdo para resposta HTTP com download
        response = HttpResponse(file_content.getvalue(), content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="leituras_{date}.txt"'
        
        # Fechar o StringIO
        file_content.close()

        return response
def Cadastro(request):

    companies = Company.objects.all()

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            full_name = form.cleaned_data['full_name']

            company = form.cleaned_data['company']

            if User.objects.filter(username=username).exists():
                messages.error(request,'Usuário já existe.')

            else:

                user = User.objects.create_user(username=username,password=password)
                nomes = full_name.split()
                user.first_name = nomes[0]

                if len(nomes) > 1:
                    user.last_name = " ".join(nomes[1:])

                user.save()

                Profile.objects.create(user=user,company=company,role='EMPLOYEE')                  
                messages.success(request,'Usuário cadastrado com sucesso.')
                return redirect('index')

    else:
        form = RegisterForm()

    return render(request,'Cadastro.html',{'form': form,'companies': companies})

@login_required
def Carma(request):

    profile = get_object_or_404(Profile, user=request.user)

    print('DEBUG >>> user:', request.user, '| user.id:', request.user.id)
    print('DEBUG >>> profile.id:', profile.id, '| profile.company:', profile.company, '| company_id:', profile.company_id)

    if profile.role == 'ADMIN':

        company_users = User.objects.filter(profile__company=profile.company,profile__role='EMPLOYEE').order_by('first_name','username')
        assignment_form = CarAssignmentForm(company=profile.company)
        assignments = CarAssignment.objects.filter(car__company=profile.company).select_related('car','user').order_by('car__identifier','-start_date')

        print('DEBUG >>> assignments.count():', assignments.count())

        return render(request,'Carma.html',{'is_admin': True,'company_users': company_users,'assignment_form': assignment_form,'assignments': assignments,})
    ...

@login_required
def Funcionario(request, user_id, date=None):

    profile = get_object_or_404(Profile, user=request.user)

    if profile.role != 'ADMIN':
        return redirect('Carma')

    selected_user = get_object_or_404(User,id=user_id,profile__company=profile.company,profile__role='EMPLOYEE')

    user_reads = Read.objects.filter(client=selected_user)

    grouped_reads = (user_reads.annotate(date=TruncDate('timestamp')).values('date').distinct().order_by('-date'))

    reads = None
    selected_date = None

    if date:
        selected_date = parse_date(date)
        if selected_date:reads = Read.objects.filter(client=selected_user,timestamp__date=selected_date).order_by('timestamp')

    return render(request, 'funcionario.html', {'selected_user': selected_user,'grouped_reads': grouped_reads,'reads': reads,'selected_date': selected_date,})


@login_required
def manage_cars(request):

    profile = get_object_or_404(Profile,user=request.user)
    if profile.role != 'ADMIN':
        return redirect('Carma')
    if request.method == 'POST':
        form = CarAssignmentForm(request.POST,company=profile.company)
        if form.is_valid():
            assignment = form.save(commit=False)
            if assignment.user.profile.company != profile.company:
                return redirect('Carma')
            if assignment.car.company != profile.company:
                return redirect('Carma')
            assignment.save()

            return redirect('Carma')
    return redirect('Carma')