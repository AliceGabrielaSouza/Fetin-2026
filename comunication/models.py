from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Company

class Car(models.Model):
    identifier = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,related_name='cars',null=True,blank=True)

    def __str__(self):
        if self.company:
            return f"{self.identifier} - {self.company.name}"
        return self.identifier
    
class CarAssignment(models.Model): #com quem esta o veiculo
    car = models.ForeignKey(Car, on_delete=models.CASCADE,related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='car_assignments')

    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.car} - {self.user} - {self.start_date} até {self.end_date}"

class Read(models.Model):
    speed = models.IntegerField(default=0)  # Campo para armazenar o status de frenagem
    braking= models.IntegerField(default=0)
    turn_signal = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)  # Data e hora da leitura
    client = models.ForeignKey(User,on_delete=models.CASCADE)
    car = models.ForeignKey(Car,on_delete=models.SET_NULL,null=True,blank=True,related_name='reads')
    def __str__(self):
        return f"speed: {self.speed}, timestamp: {self.timestamp}, turn_signal: {self.turn_signal}, braking: {self.braking}, client:{self.client}, car:{self.car}"
        