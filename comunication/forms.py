from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Car, CarAssignment


class CarAssignmentForm(forms.ModelForm):

    class Meta:
        model = CarAssignment

        fields = ['car','user','start_date','end_date']
        widgets = {'start_date': forms.DateInput(attrs={'type': 'date'}),'end_date': forms.DateInput(attrs={'type': 'date'}),}

    def __init__(self, *args, company=None, **kwargs):

        super().__init__(*args, **kwargs)

        if company:
            self.fields['car'].queryset = Car.objects.filter(company=company).order_by('identifier')
            self.fields['user'].queryset = User.objects.filter(profile__company=company,profile__role='EMPLOYEE').order_by('first_name','username')

    def clean(self):

        cleaned_data = super().clean()
        car = cleaned_data.get('car')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if (start_date and end_date and start_date > end_date): 
            raise ValidationError(
                'A data inicial não pode ser maior que a data final.'
            )

        if car and start_date and end_date:
            existing_assignments = CarAssignment.objects.filter(car=car,start_date__lte=end_date,end_date__gte=start_date)

            if self.instance.pk:existing_assignments = existing_assignments.exclude(
                    pk=self.instance.pk
                )

            if existing_assignments.exists():raise ValidationError(
                    'Este carro já está atribuído a outro funcionário nesse período.'
                )

        return cleaned_data