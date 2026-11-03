from rest_framework.exceptions import ValidationError
from datetime import datetime


def _parse_fechas(request):
    desde = request.query_params.get("desde")
    hasta = request.query_params.get("hasta")

    if not desde or not hasta:
        raise ValidationError({
            "detail": "Los parámetros 'desde' y 'hasta' son obligatorios (YYYY-MM-DD)."
        })

    try:
        desde_dt = datetime.strptime(desde, "%Y-%m-%d").date()
        hasta_dt = datetime.strptime(hasta, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError({
            "detail": "Formato de fecha inválido. Usá YYYY-MM-DD."
        })

    if desde_dt > hasta_dt:
        raise ValidationError({
            "detail": "'desde' no puede ser mayor que 'hasta'."
        })

    return desde_dt, hasta_dt
