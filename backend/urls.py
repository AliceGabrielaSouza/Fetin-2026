from django.urls import path
from backend import views
from .views import index, History, ONU, Contact, Login, Carma, Cadastro, read_by_date


urlpatterns = [
    path('', index, name="index"),
    path('index', index, name="index"),
    path('History', History, name="History"),
    path('ONU', ONU, name="ONU"),
    path('Contact', Contact, name="Contact"),
    path('Login', Login, name="Login"),
    path('Cadastro', Cadastro, name="Cadastro"),
    path('read_by_date/<str:date>/', read_by_date, name='Information'),
    path('save-txt/<date>/', views.save_txt, name='save_txt'),
    path('Carma/',views.Carma,name='Carma'),
    path('Carma/<int:user_id>/',views.Carma,name='Carma_user'),
    path('Carma/<int:user_id>/<str:date>/',views.Carma,name='Carma_user_date'),
    path('Carma/user/<int:user_id>/',views.Funcionario,name='Carma_user'),
    path('Funcionario/<int:user_id>/',views.Funcionario,name='Funcionario'),
    path('Funcionario/<int:user_id>/<str:date>/',views.Funcionario,name='Funcionario_date'),
    path('gerenciar-carros/',views.manage_cars,name='manage_cars'),
    path('read_by_date/<str:date>/', views.read_by_date, name='read_by_date'),
    path('save-txt/<str:date>/', views.save_txt, name='save_txt'),
]