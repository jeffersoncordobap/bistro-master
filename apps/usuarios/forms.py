from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm

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
    
    
class LoginForm(forms.Form):

    username = forms.CharField(

        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }
        )

    )

    password = forms.CharField(

        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Contraseña'
            }
        )

    )
    
    
class UsuarioForm(UserCreationForm):

    class Meta:

        model = Usuario

        fields = [
            'username',
            'email',
            'cedula',
            'telefono',
            'rol',
            'password1',
            'password2'
        ]

    def __init__(self, *args, restaurante=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.restaurante = restaurante

        self.fields['rol'].choices = [
            choice for choice in self.fields['rol'].choices
            if choice[0] not in [
                Usuario.Roles.ADMIN,
                Usuario.Roles.CAJERO
            ]
        ]

        for nombre, field in self.fields.items():

            if nombre == 'rol':

                field.widget.attrs.update({
                    'class': 'form-select'
                })

            else:

                field.widget.attrs.update({
                    'class': 'form-control'
                })
    
    def clean(self):

        cleaned_data = super().clean()

        cedula = cleaned_data.get('cedula')

        if cedula:

            existe = Usuario.objects.filter(
                restaurante=self.restaurante,
                cedula=cedula
            ).exists()

            if existe:

                self.add_error(
                    'cedula',
                    'Ya existe un usuario con esta cédula.'
                )

        return cleaned_data
    
class UsuarioUpdateForm(forms.ModelForm):

    class Meta:

        model = Usuario

        fields = [
            'username',
            'email',
            'cedula',
            'telefono',
            'rol'
        ]
    
    def __init__(self, *args, restaurante=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.restaurante = restaurante

        self.fields['rol'].choices = [
            choice for choice in self.fields['rol'].choices
            if choice[0] not in [
                Usuario.Roles.ADMIN,
                Usuario.Roles.CAJERO
            ]
        ]

        for nombre, field in self.fields.items():

            if nombre == 'rol':

                field.widget.attrs.update({
                    'class': 'form-select'
                })

            else:

                field.widget.attrs.update({
                    'class': 'form-control'
                })
                
    def clean(self):

        cleaned_data = super().clean()

        cedula = cleaned_data.get('cedula')

        if cedula:

            existe = Usuario.objects.filter(
                restaurante=self.restaurante,
                cedula=cedula
            ).exclude(
                id=self.instance.id
            ).exists()

            if existe:

                self.add_error(
                    'cedula',
                    'Ya existe un usuario con esta cédula.'
                )

        return cleaned_data
    
    
class CustomPasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control'
        })