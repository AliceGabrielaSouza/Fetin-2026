from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Company
from .models import Car, CarAssignment, Read


class MakeReadTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Empresa de teste')
        user = User.objects.create_user(username='funcionario', password='senha')
        self.car = Car.objects.create(identifier='Carro_TESTE', company=company)
        CarAssignment.objects.create(
            car=self.car,
            user=user,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
        )
        self.client = APIClient()

    def test_saves_read_using_car_identifier(self):
        response = self.client.post('/Make_Read/', {
            'speed': 50,
            'braking': 1,
            'turn_signal': 0,
            'car': 'Carro_TESTE',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Read.objects.count(), 1)

    def test_rejects_read_without_current_assignment(self):
        CarAssignment.objects.update(end_date=date.today() - timedelta(days=1))
        response = self.client.post('/Make_Read', {
            'speed': 50, 'braking': 1, 'turn_signal': 0, 'car': self.car.pk,
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Read.objects.count(), 0)
