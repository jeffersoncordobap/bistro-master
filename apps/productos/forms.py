from django import forms

from apps.productos.models import Producto, CategoriaProducto


class ProductoForm(forms.ModelForm):

    class Meta:

        model = Producto

        fields = [
            'categoria',
            'nombre',
            'descripcion',
            'precio',
            'imagen',
            'disponible',
            'control_stock',
            'stock',
            'cantidad_maxima_por_pedido',
            'cubierto_por_tiquetera'
        ]

    def __init__(self, *args, **kwargs):

        restaurante = kwargs.pop('restaurante', None)

        super().__init__(*args, **kwargs)

        if restaurante:

            self.fields['categoria'].queryset = restaurante.categorias.all()

        for nombre, field in self.fields.items():

            if isinstance(field.widget, forms.CheckboxInput):

                field.widget.attrs.update({
                    'class': 'form-check-input'
                })

            elif isinstance(field.widget, forms.Select):

                field.widget.attrs.update({
                    'class': 'form-select'
                })

            elif isinstance(field.widget, forms.FileInput):

                field.widget.attrs.update({
                    'class': 'form-control'
                })

            else:

                field.widget.attrs.update({
                    'class': 'form-control'
                })

        self.fields['precio'].widget.attrs.update({
            'min': '0',
            'step': '0.01'
        })

        self.fields['stock'].widget.attrs.update({
            'min': '0'
        })
        
        
class CategoriaProductoForm(forms.ModelForm):

    class Meta:

        model = CategoriaProducto

        fields = [
            'nombre',
            'activa'
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for nombre, field in self.fields.items():

            if isinstance(field.widget, forms.CheckboxInput):

                field.widget.attrs.update({
                    'class': 'form-check-input'
                })

            else:

                field.widget.attrs.update({
                    'class': 'form-control'
                })