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
            'estado'
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for nombre, field in self.fields.items():

            if isinstance(field.widget, forms.Select):

                field.widget.attrs.update({
                    'class': 'form-select form-select-lg rounded-3'
                })

            else:

                field.widget.attrs.update({
                    'class': 'form-control form-control-lg rounded-3',
                    'placeholder': f'Ingrese {field.label.lower()}'
                })  