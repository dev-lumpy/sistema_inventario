from django.shortcuts import render

# Create your views here.
def start_login(request):
    return render(request, 'login.html')
