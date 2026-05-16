from django.shortcuts import redirect


def rol_requerido(roles_permitidos):

    def decorator(view_func):

        def wrapper(request, *args, **kwargs):

            if request.user.rol in roles_permitidos:

                return view_func(
                    request,
                    *args,
                    **kwargs
                )

            return redirect('login')

        return wrapper

    return decorator