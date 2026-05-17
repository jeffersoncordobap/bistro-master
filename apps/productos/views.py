from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages

from apps.productos.forms import ProductoForm,CategoriaProductoForm
from apps.productos.models import Producto, CategoriaProducto


def lista_productos(request):

    productos = Producto.objects.filter(
        restaurante=request.user.restaurante
    ).order_by('-creado')

    context = {
        'productos': productos
    }

    return render(
        request,
        'dashboard/productos/lista_productos.html',
        context
    )
    
    
def crear_producto(request):

    if request.method == 'POST':

        form = ProductoForm(
            request.POST,
            request.FILES,
            restaurante=request.user.restaurante
        )

        if form.is_valid():

            producto = form.save(commit=False)

            producto.restaurante = request.user.restaurante

            producto.save()

            messages.success(
                request,
                'Producto creado correctamente.'
            )

            return redirect('lista_productos')

    else:

        form = ProductoForm(
            restaurante=request.user.restaurante
        )

    context = {
        'form': form
    }

    return render(
        request,
        'dashboard/productos/crear_producto.html',
        context
    )

def editar_producto(request, producto_id):

    producto = get_object_or_404(
        Producto,
        id=producto_id,
        restaurante=request.user.restaurante
    )

    if request.method == 'POST':

        form = ProductoForm(
            request.POST,
            request.FILES,
            instance=producto,
            restaurante=request.user.restaurante
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Producto actualizado correctamente.'
            )

            return redirect('lista_productos')

    else:

        form = ProductoForm(
            instance=producto,
            restaurante=request.user.restaurante
        )

    context = {
        'form': form,
        'producto': producto
    }

    return render(
        request,
        'dashboard/productos/editar_producto.html',
        context
    )

def toggle_disponibilidad_producto(request, producto_id):

    producto = get_object_or_404(
        Producto,
        id=producto_id,
        restaurante=request.user.restaurante
    )

    producto.disponible = not producto.disponible

    producto.save()

    if producto.disponible:

        messages.success(
            request,
            f'{producto.nombre} ahora está disponible.'
        )

    else:

        messages.warning(
            request,
            f'{producto.nombre} fue marcado como no disponible.'
        )

    return redirect('lista_productos')

def lista_categorias(request):

    categorias = CategoriaProducto.objects.filter(
        restaurante=request.user.restaurante
    )

    context = {
        'categorias': categorias
    }

    return render(
        request,
        'dashboard/productos/lista_categorias.html',
        context
    )
    
def crear_categoria(request):

    if request.method == 'POST':

        form = CategoriaProductoForm(request.POST)

        if form.is_valid():

            categoria = form.save(commit=False)

            categoria.restaurante = request.user.restaurante

            categoria.save()

            messages.success(
                request,
                'Categoría creada correctamente.'
            )

            return redirect('lista_categorias')

    else:

        form = CategoriaProductoForm()

    context = {
        'form': form
    }

    return render(
        request,
        'dashboard/productos/crear_categoria.html',
        context
    )
    
def editar_categoria(request, categoria_id):

    categoria = get_object_or_404(
        CategoriaProducto,
        id=categoria_id,
        restaurante=request.user.restaurante
    )

    if request.method == 'POST':

        form = CategoriaProductoForm(
            request.POST,
            instance=categoria
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Categoría actualizada correctamente.'
            )

            return redirect('lista_categorias')

    else:

        form = CategoriaProductoForm(
            instance=categoria
        )

    context = {
        'form': form,
        'categoria': categoria
    }

    return render(
        request,
        'dashboard/productos/editar_categoria.html',
        context
    )    
    
def toggle_categoria(request, categoria_id):

    categoria = get_object_or_404(
        CategoriaProducto,
        id=categoria_id,
        restaurante=request.user.restaurante
    )

    categoria.activa = not categoria.activa

    categoria.save()

    messages.success(
        request,
        'Estado categoría actualizado.'
    )

    return redirect('lista_categorias')


