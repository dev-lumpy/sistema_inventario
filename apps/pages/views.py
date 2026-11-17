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


def _moneda_para(rol: str, usuario_id) -> str:
    from apps.accounts.models import Administrador, VendedorAdministrador

    if rol == "administrador":
        administrador = Administrador.objects.filter(pk=usuario_id).first()
        return administrador.moneda if administrador else "BOB"
    if rol == "vendedor":
        vinculo = (
            VendedorAdministrador.objects.filter(
                vendedor_id=usuario_id,
                estado="aceptado",
            )
            .select_related("administrador")
            .order_by("creado_en")
            .first()
        )
        return vinculo.administrador.moneda if vinculo else "BOB"
    return "BOB"


def dashboard_page(request):
    rol = request.session.get("rol")
    nombre = request.session.get("nombre", "")
    usuario_id = request.session.get("usuario_id", "")
    moneda = _moneda_para(rol, usuario_id) if usuario_id else "BOB"

    if rol == "administrador":
        return render(
            request,
            "administrador/index.html",
            {
                "nombre": nombre,
                "rol": rol,
                "user_id": str(usuario_id),
                "moneda": moneda,
            },
        )
    if rol == "vendedor":
        return render(
            request,
            "vendedor/index.html",
            {
                "nombre": nombre,
                "rol": rol,
                "user_id": str(usuario_id),
                "moneda": moneda,
            },
        )
    return redirect("pages:login")


def logout_page(request):
    request.session.flush()
    return redirect("pages:login")
