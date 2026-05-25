from django import forms
from django.utils import timezone

from .models import Tiquetera, PlanTiquetera


class HistorialTiqueteraFiltroForm(forms.Form):

    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del cliente'
        })
    )

    def clean(self):
        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise forms.ValidationError(
                'La fecha final debe ser mayor o igual a la fecha inicial.'
            )

        return cleaned_data


class TiqueteraForm(forms.ModelForm):

    class Meta:
        model = Tiquetera

        fields = [
            'plan',
            'cliente_nombre',
            'cliente_telefono',
            'fecha_inicio',
            'fecha_vencimiento',
        ]

        widgets = {
            'plan': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'cliente_nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre del cliente'
                }
            ),

            'cliente_telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Número telefónico'
                }
            ),

            'fecha_inicio': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'fecha_vencimiento': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            )
        }

    def __init__(self, *args, restaurante=None, **kwargs):
        super().__init__(*args, **kwargs)

        if restaurante:
            self.fields['plan'].queryset = PlanTiquetera.objects.filter(
                restaurante=restaurante,
                activo=True
            )

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data['fecha_inicio']

        if fecha_inicio < timezone.now().date():
            raise forms.ValidationError(
                'La fecha de inicio no puede ser menor al día actual.'
            )

        return fecha_inicio

    def clean(self):
        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')

        if (
            fecha_inicio and
            fecha_vencimiento and
            fecha_vencimiento <= fecha_inicio
        ):
            raise forms.ValidationError(
                'La fecha de vencimiento debe ser mayor a la fecha de inicio.'
            )

        return cleaned_data
    
    
class PlanTiqueteraForm(forms.ModelForm):

    class Meta:
        model = PlanTiquetera

        fields = [
            'nombre',
            'descripcion',
            'precio',
            'cantidad_consumos',
            'dias_vigencia',
            'tipo_servicio',
            'permite_multiples_consumos',
            'activo'
        ]

        widgets = {

            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Tiquetera Almuerzo Mensual'
            }),

            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del plan'
            }),

            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 120000'
            }),

            'cantidad_consumos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),

            'dias_vigencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),

            'tipo_servicio': forms.Select(attrs={
                'class': 'form-select'
            }),

            'permite_multiples_consumos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

        }

    def clean_precio(self):

        precio = self.cleaned_data['precio']

        if precio <= 0:
            raise forms.ValidationError(
                'El precio debe ser mayor a cero.'
            )

        return precio

    def clean_cantidad_consumos(self):

        cantidad = self.cleaned_data['cantidad_consumos']

        if cantidad <= 0:
            raise forms.ValidationError(
                'La cantidad de consumos debe ser mayor a cero.'
            )

        return cantidad