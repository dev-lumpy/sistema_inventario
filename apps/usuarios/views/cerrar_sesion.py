from rest_framework.response import Response
from rest_framework.views import APIView

class CerrarSesion(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        response = Response({'status': 'ok'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
