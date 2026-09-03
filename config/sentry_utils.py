from contextvars import ContextVar

import sentry_sdk

_sentry_manual = ContextVar("sentry_manual", default=False)


def sentry_before_send(event, hint):
    """Solo envía eventos que fueron capturados explícitamente via capture_exception()."""
    return event if _sentry_manual.get() else None


def capture_exception(exc_info=None):
    """Envía una excepción a Sentry manualmente.

    Úsala en lugar de sentry_sdk.capture_exception() para que el
    filtro before_send la deje pasar.

    Ejemplo:
        try:
            ...
        except Exception as e:
            capture_exception(e)
    """
    token = _sentry_manual.set(True)
    try:
        sentry_sdk.capture_exception(exc_info)
    finally:
        _sentry_manual.reset(token)