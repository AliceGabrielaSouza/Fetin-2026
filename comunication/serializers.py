from rest_framework import serializers
from .models import Car, Read
from rest_framework import viewsets

class ReadSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())
    # O funcionário é definido pela atribuição do carro, não pelo dispositivo.
    client = serializers.CharField(source='client.username', read_only=True)
    # A empresa é derivada do carro para evitar duplicar essa informação em Read.
    company = serializers.SerializerMethodField()

    def get_company(self, obj):
        # Uma leitura sem carro ainda pode existir por causa de dados antigos.
        if obj.car and obj.car.company:
            return obj.car.company.name
        return None

    class Meta:
        model = Read
        fields = ['speed', 'braking', 'turn_signal', 'car', 'client', 'company']

    def to_internal_value(self, data):
        data = data.copy()
        car_value = data.get('car')
        if car_value in (None, '') and data.get('car_identifier') not in (None, ''):
            car_value = data['car_identifier']
        if isinstance(car_value, str) and not car_value.isdigit():
            car = Car.objects.filter(identifier=car_value).first()
            if car is None:
                raise serializers.ValidationError({'car': 'Carro não encontrado.'})
            data['car'] = car.pk
        return super().to_internal_value(data)
