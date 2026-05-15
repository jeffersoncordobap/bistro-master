from django import forms

from .models import Restaurante

class RestauranteForm(forms.ModelForm):

    class Meta:
        model = Restaurante

        fields = [
            'nombre',
            'nit',
            'direccion',
            'telefono'
        ]

        widgets = {

            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre del restaurante'
                }
            ),

            'nit': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'NIT'
                }
            ),

            'direccion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Dirección'
                }
            ),

            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Teléfono'
                }
            ),

        }