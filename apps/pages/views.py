# apps/pages/views.py
from typing import Optional

from django.shortcuts import render, redirect
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


def _tiene_token_valido(request) -> Optional[dict]:
    """Helper: comprueba si el request trae un access_token válido en cookie.
     y retorna el rol"""
    raw_token = request.COOKIES.get('access_token')
    if not raw_token:
        return None
    try:
        token = AccessToken(raw_token)
        return {
            'rol': token['rol'],
            'nombre': token['username']
        }
    except (TokenError, KeyError):
        return None

def index(request):
    if _tiene_token_valido(request):
        return redirect('pages:dashboard') 
    return redirect('pages:login')


def login_page(request):
    if _tiene_token_valido(request):
        return redirect('pages:dashboard') 
    return render(request, 'login.html')


def register_page(request):
    if _tiene_token_valido(request):
        return redirect('pages:dashboard') 
    return render(request, 'crear-cuenta.html')


def dashboard_page(request):
    info = _tiene_token_valido(request)

    if not info:
        return redirect('pages:login')

    
    rol    = info['rol']
    nombre = info['nombre']

    if rol == 'administrador':
        return render(
            request, 'administrador/index.html',
            {'nombre': nombre, 'rol': rol}
        )
    if rol == 'vendedor':
        return render(
            request, 'vendedor/index.html',
            {'nombre': nombre, 'rol': rol}
        )

    raise ValueError("Rol inexistente")
