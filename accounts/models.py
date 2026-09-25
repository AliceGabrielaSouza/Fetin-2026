from django.db import models
from django.contrib.auth.models import User

class Company(models.Model): #cria uma tabela somente com as empresas
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    
class Profile(models.Model): #cria uma tabela relacionando os funcionarios com as empresas e guarda se são administrador ou funcionario

    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('EMPLOYEE', 'Funcionario'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='EMPLOYEE'
    )

    def __str__(self):
        return self.user.username