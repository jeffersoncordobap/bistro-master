from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class RegistroAdministradorForm(UserCreationForm):

    class Meta:
        model = Usuario

        fields = [
            'username',
            'email',
            'cedula',
            'telefono',
            'password1',
            'password2'
        ]

        widgets = {

            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre de usuario'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Correo electrónico'
                }
            ),

            'cedula': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Cédula'
                }
            ),

            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Teléfono'
                }
            ),

        }

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Contraseña'
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirmar contraseña'
            }
        )
    )