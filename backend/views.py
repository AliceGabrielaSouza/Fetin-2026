from datetime import datetime
import io

from pathlib import Path
import re
from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.db.models.functions import TruncDate

from django.contrib.auth.models import User
from django.contrib import messages

from accounts.models import Company, Profile
from accounts.forms import RegisterForm

from comunication.models import Read, CarAssignment
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

def videos_for_user_date(user, selected_date):
    filename_prefix = f'{user.username}_{selected_date:%Y_%m_%d}' #identifica o prefixo de data do video
    video_pattern = re.compile(rf'^{re.escape(filename_prefix)}(?:_(\d+))?(?:\.[^.]+)?$')
    videos = {}

    # Aceita vídeos já existentes na raiz de midia e uploads na subpasta videos.
    video_dirs = [Path(settings.MEDIA_ROOT) / 'videos', Path(settings.MEDIA_ROOT)]
    for videos_dir in video_dirs:
        for video_path in videos_dir.glob(f'{filename_prefix}*'):
            if video_path.is_file():
                match = video_pattern.match(video_path.name)
                if match:
                    video_number = int(match.group(1) or 1)
                    relative_path = video_path.relative_to(settings.MEDIA_ROOT).as_posix()
                    video_url = f'{settings.MEDIA_URL.rstrip("/")}/{relative_path}'
                    videos.setdefault(video_number, video_url)

    return videos

#colocar os videos em ordem
def add_video_urls(user_reads, user, selected_date):
    named_videos = videos_for_user_date(user, selected_date)
    ordered_reads = list(user_reads.order_by('timestamp', 'id'))

    for position, read in enumerate(ordered_reads, start=1):
        read.video_url = named_videos.get(position)

    return ordered_reads

def reads_for_user_date(user, selected_date):
    local_date = TruncDate('timestamp', tzinfo=timezone.get_current_timezone())
    return Read.objects.filter(client=user).annotate(
        local_date=local_date
    ).filter(local_date=selected_date)

def read_by_date(request, date):
    # Filtra as leituras pela data local e adiciona os vídeos correspondentes.
    selected_date = datetime.strptime(date, '%Y-%m-%d').date()
    user_reads = reads_for_user_date(request.user, selected_date)
    user_reads = add_video_urls(user_reads, request.user, selected_date)

    return render(request, 'Information.html', {
        'user_reads': user_reads,
        'selected_date': selected_date,
    })

def save_txt(request, date):
    if request.method == 'GET':
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        day = Read.objects.filter(client=request.user, timestamp__date=selected_date)

        if not day.exists():
            return HttpResponse("Nenhuma leitura encontrada para o dia de hoje.")

        file_content = io.StringIO()

        for read in day:
            line = ""
            if read.speed == 1:
                line += f"Velocidade: {read.speed} km/h, "

            if read.braking == 1:
                line += "Freio ativado "

            if read.turn_signal != 0:
                line += "Seta Ligada"

            if line:
                line += f"  Timestamp: {read.timestamp}\n"
                file_content.write(line)

        response = HttpResponse(file_content.getvalue(), content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="leituras_{date}.txt"'
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

    if profile.role == 'ADMIN':

        company_users = User.objects.filter(profile__company=profile.company,profile__role='EMPLOYEE').order_by('first_name','username')
        assignment_form = CarAssignmentForm(company=profile.company)
        assignments = CarAssignment.objects.filter(car__company=profile.company,user__profile__company=profile.company).select_related('car','user').order_by('car__identifier','-start_date')

        return render(request,'Carma.html',{'is_admin': True,'company_users': company_users,'assignment_form': assignment_form,'assignments': assignments,})


    user_reads = Read.objects.filter(client=request.user)
    grouped_reads = (user_reads.annotate(date=TruncDate('timestamp')).values('date').distinct().order_by('-date'))

    return render(request,'Carma.html',{'is_admin': False,'selected_user': request.user,'grouped_reads': grouped_reads,})


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
        if selected_date:
            # O administrador só chega aqui para funcionários da própria empresa.
            reads = reads_for_user_date(selected_user, selected_date)
            # Reutiliza o padrão de nomes dos vídeos do funcionário selecionado.
            reads = add_video_urls(reads, selected_user, selected_date)

    return render(request, 'Funcionario.html', {'selected_user': selected_user,'grouped_reads': grouped_reads,'reads': reads,'selected_date': selected_date,})

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