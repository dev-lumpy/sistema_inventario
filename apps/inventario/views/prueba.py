from django.http import HttpResponse

def index(request):
    return HttpResponse("Llamaste exitosamente al endpoint.", status=200)
