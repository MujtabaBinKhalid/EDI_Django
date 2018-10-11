from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
import socket
import schedule
import time
import glob


def index(request):
    """ If the request is get it will return a login form , other wise it send a tcp login request to server. """
    if request.method == "GET":
        return render(request, 'Login/index.html')

    elif request.method == "POST":
        try:
            loginStatus = request.POST['option']
            response = "login_company"
            responseValue = authentication(request, "35.161.234.96", 9991, 1024, "login_company")
        except Exception as e:
            response = "login_user"
            responseValue = authentication(request, "35.161.234.96", 9991, 1024, "login_user")

        if(responseValue == "Success"):
            httpresponse = HttpResponse(responseValue)
            settingCookie(request, httpresponse)
            return redirect("main:index")
        else:
            return redirect(request, 'Login/index.html')


def authentication(request, ip_address, port_number, bufferSize, messageType):
    """ It is used to authenticate the user/company and returns the request status. """
    data = {}
    TCP_IP = ip_address
    TCP_PORT = port_number
    BUFFER_SIZE = bufferSize
    data['message_type'] = messageType
    data['email'] = request.POST['username']
    data['password'] = request.POST['pass']
    json_data = json.dumps(data)
    MESSAGE = json_data
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((TCP_IP, TCP_PORT))
    tcp_socket.sendto(MESSAGE.encode(), (TCP_IP, TCP_PORT))
    data = tcp_socket.recv(BUFFER_SIZE)
    tcp_socket.close()
    responseInstring = data.decode("utf-8")
    json_acceptable_string = responseInstring.replace("'", "\"")
    dictionary = json.loads(json_acceptable_string)
    return dictionary["status"]


def settingCookie(request, response):
    """ Setting the cookie to store the email of the login id and then use it to fetch all comapnies."""
    response.set_cookie("user_email", request.POST['username'])
    return response
