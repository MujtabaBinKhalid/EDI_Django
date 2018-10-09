from django.shortcuts import render


def index(request):
    """ Index page, after login """
    if request.method == "GET":
        return render(request, 'main/index.html')


def accountCreation(request):
    """ It will display the registration form to make an account"""
    return render(request, 'main/edi_registration.html')
