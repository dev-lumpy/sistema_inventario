import json
import logging

logger = logging.getLogger(__name__)


def debug_requests_middleware(get_response):
    def middleware(request):
        # ---------- ANTES de la vista ----------
        print("=" * 60)
        print(f"[REQ] {request.method} {request.path}")
        print(f"  IP: {request.META.get('REMOTE_ADDR')}")
        print(f"  Content-Type: {request.content_type}")

        # Headers (los que importan)
        for h in ('Authorization', 'Cookie', 'X-CSRFToken'):
            valor = request.META.get(f'HTTP_{h.upper().replace("-", "_")}')
            if valor:
                print(f"  {h}: {valor[:80]}{'...' if len(str(valor)) > 80 else ''}")

        # Query params
        if request.GET:
            print(f"  GET: {dict(request.GET)}")

        # Body (JSON, form, etc.)
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            if request.content_type == 'application/json':
                try:
                    print(f"  BODY: {json.dumps(request.body and json.loads(request.body), ensure_ascii=False, indent=2)}")
                except Exception as e:
                    print(f"  BODY (raw): {request.body[:200]!r}  (no es JSON: {e})")
            elif request.content_type == 'application/x-www-form-urlencoded':
                print(f"  POST: {dict(request.POST)}")

        # ---------- Después de la vista ----------
        response = get_response(request)

        print(f"[RES] {response.status_code} {request.method} {request.path}")

        # Si es JSON y no es muy grande, mostralo
        if response.get('Content-Type', '').startswith('application/json'):
            try:
                body = response.content.decode('utf-8')
                data = json.loads(body)
                preview = json.dumps(data, ensure_ascii=False, indent=2)
                if len(preview) > 800:
                    preview = preview[:800] + '\n  ... (truncado)'
                print(f"  RES BODY: {preview}")
            except Exception:
                pass

        print("=" * 60)
        return response

    return middleware
