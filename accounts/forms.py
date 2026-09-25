from django import forms
from accounts.models import Company


class RegisterForm(forms.Form):

    full_name = forms.CharField(
        max_length=100,
        label='Nome completo'
    )

    username = forms.CharField(
        max_length=50,
        label='Username'
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='Senha'
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label='Confirmar senha'
    )

    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        label='Empresa'
    )

    def clean_username(self):
        username = self.cleaned_data['username']

        from django.contrib.auth.models import User

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                'Este username já está cadastrado.'
            )

        return username

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    'As senhas não coincidem.'
                )

        return cleaned_data