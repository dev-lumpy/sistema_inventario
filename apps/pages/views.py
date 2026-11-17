from django.shortcuts import redirect, render


def index(request):
    return redirect("pages:login")


def login_page(request):
    if request.session.get("rol"):
        return redirect("pages:dashboard")
    return render(request, "login.html")


def register_page(request):
    if request.session.get("rol"):
        return redirect("pages:dashboard")
    return render(request, "crear-cuenta.html")


def dashboard_page(request):
    rol = request.session.get("rol")
    nombre = request.session.get("nombre", "")
    usuario_id = request.session.get("usuario_id", "")

    if rol == "administrador":
        return render(
            request,
            "administrador/index.html",
            {"nombre": nombre, "rol": rol, "user_id": str(usuario_id)},
        )
    if rol == "vendedor":
        return render(
            request,
            "vendedor/index.html",
            {"nombre": nombre, "rol": rol, "user_id": str(usuario_id)},
        )
    return redirect("pages:login")


def logout_page(request):
    request.session.flush()
    return redirect("pages:login")
