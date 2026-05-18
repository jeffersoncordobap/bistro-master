import re

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


class RestauranteUpdateForm(forms.ModelForm):

    class Meta:
        model = Restaurante

        fields = [
            'nombre',
            'direccion',
            'telefono',
            'estado',
            'slogan',
            'logo',
            'portada',
            'color_principal',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for nombre, field in self.fields.items():

            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'form-select form-select-lg rounded-3'
                })
            elif isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': 'form-control form-control-lg rounded-3',
                    'placeholder': f'Ingrese {field.label.lower()}'
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'form-control rounded-3',
                    'rows': 3,
                    'placeholder': f'Ingrese {field.label.lower()}'
                })
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({
                    'class': 'form-control rounded-3'
                })

        # Widget especial para el color
        self.fields['color_principal'].widget = forms.TextInput(
            attrs={
                'type': 'color',
                'class': 'form-control form-control-color rounded-3',
                'style': 'width: 80px; height: 48px; padding: 4px;'
            }
        )

        # Slogan como textarea corto
        self.fields['slogan'].widget = forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'Ej: La mejor cocina casera de la ciudad'
            }
        )

    def clean_color_principal(self):
        color = (self.cleaned_data.get('color_principal') or '').strip()
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise forms.ValidationError('Ingresa un color válido en formato HEX (ej: #e74c3c).')
        return color.lower()