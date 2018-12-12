from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import json
import socket
import schedule
import time
import glob
import datetime
import requests
from ast import literal_eval

def index(request):
    """ If the request is get it will return a login form , other wise it send a tcp login request to server. """
    if request.method == "GET":
        try:
            sessionData = request.session['name']
            return redirect("main:index")
        except Exception as e:
            return render(request, 'Login/index.html')

    elif request.method == "POST":
        try:
            loginStatus = request.POST['option']
            request.session['userStatus'] = "login_company"
            response = "login_company"
            responseValue = authentication(request)
        except Exception as e:
            request.session['userStatus'] = "login_user"
            response = "login_user"
            python_dict = authentication(request)

        if(python_dict.get("access_token", "empty") != "empty"):
            
            request.session['name'] = request.POST['username']
            request.session['token'] = python_dict.get("access_token", "empty")
            # httpresponse = HttpResponse(python_dict)
            # settingCookie("user_email",request.POST['username'], httpresponse)
            # settingCookie("token",(python_dict.get("access_token", "empty"), httpresponse)
            # set_cookie(httpresponse, "email_user", request.POST['username'])
            return redirect("main:index")
        else:
           
             return render(request, 'Login/index.html', {"error": "login credentials are not valid"})


def authentication(request):
    # It is used to authenticate the user/company and returns the request status.
    url = "https://api.coldwhere.com/oauth/token"
    username= request.POST['username']
    password = request.POST['pass']
    payload = "grant_type=password&username=" + username + "&password=" + password + "&client_id=spring-security-oauth2-read-write-client&undefined="
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Authorization': "Basic c3ByaW5nLXNlY3VyaXR5LW9hdXRoMi1yZWFkLXdyaXRlLWNsaWVudDpzcHJpbmctc2VjdXJpdHktb2F1dGgyLXJlYWQtd3JpdGUtY2xpZW50LXBhc3N3b3JkMTIzNA==",
        'cache-control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    return  literal_eval(response.text)
    

def settingCookie(cookieName,request, response):
    """ Setting the cookie to store the email of the login id and then use it to fetch all comapnies."""
    response.set_cookie(cookieName, request)


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow(
    ) + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
