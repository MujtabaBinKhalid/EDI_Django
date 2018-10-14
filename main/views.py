from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from main.models import EDIAccount


def index(request):
    """ Index page, after login """
    if request.method == "GET":
        return render(request, 'main/index.html')


def accountCreation(request):
    """ It will display the registration form to make an account"""
    if request.is_ajax() or request.method == 'POST':
        # return HttpResponse(request.COOKIES.get('user_email'))
        edi_account = EDIAccount.objects.create(ipHost=request.POST['iphost'], userName=request.POST['username'],
                                                password=request.POST['password'], email="request.COOKIES.get('user_email')", input_path=request.POST['inputpath'],
                                                output_path=request.POST['outputpath'], ip_hostOut=request.POST['iphostOut'],
                                                passwordOut=request.POST['passwordOut'],  user_nameOut=request.POST['usernameOut'])
        edi_account.save()
        # return HttpResponse(request.COOKIES.get('user_email'))
        return HttpResponse("Data inserted Sucessfully")
    elif request.method == "GET":
        return render(request, 'main/edi_registration.html', {'cookie_email':  request.COOKIES.get('user_email')})
