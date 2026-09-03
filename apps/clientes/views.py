from django.shortcuts import render

# Create your views here.
def dashboard(request):
    return render(request, 'index.html')

def error_500(request):
    return render(request, 'error-500.html')
