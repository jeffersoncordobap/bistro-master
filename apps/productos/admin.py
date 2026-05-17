from django.contrib import admin

from apps.productos.models import (
    CategoriaProducto,
    Producto
)


admin.site.register(CategoriaProducto)
admin.site.register(Producto)
