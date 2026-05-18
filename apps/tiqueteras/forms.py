from django import forms
from django.utils import timezone

from .models import Tiquetera, PlanTiquetera


class TiqueteraForm(forms.ModelForm):

    class Meta:
        model = Tiquetera

        fields = [
            'plan',
            'cliente_nombre',
            'cliente_telefono',
            'fecha_inicio',
            'fecha_vencimiento',
            'activa'
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
            ),

            'activa': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
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