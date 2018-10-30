from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from main.models import accountRegistration

import ftplib
import time
import json
import socket


def generatingReport(request):
    # try:
    # return HttpResponse(request.session['company_email'])
    accountDetail = accountRegistration.objects.get(email=request.session['company_email'])
    # return HttpResponse(accountDetail.password)

    ftp_companyLogin = ftplib.FTP(
        accountDetail.ipHost, accountDetail.userName, accountDetail.password)
    return HttpResponse(ftp_companyLogin.getwelcome())
    #
    #     # if accountDetail:
    #     #     result = fetchingLatLong(request, accountDetail)
    #     #     creatingOutputFile(accountDetail, request, result.get('location_lat'),
    #     #                        result.get('location_long'),  str(request.POST['file_name']))
    # except Exception as e:
    #     return HttpResponse("No Ftp Account is associated with it.")

#
# def fetchingLatLong(request, accountDetail):
#     TCP_IP = "34.213.95.106"
#     TCP_PORT = 9991
#     BUFFER_SIZE = 1024
#     data = {}
#     data['message_type'] = 'current_load_info'
#     data['id_device_load_record'] = str(request.POST['device_record'])
#     json_data = json.dumps(data)
#     MESSAGE = json_data
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((TCP_IP, TCP_PORT))
#     s.sendto(MESSAGE.encode(), (TCP_IP, TCP_PORT))
#     data = s.recv(BUFFER_SIZE)
#     s.close()
#     responseInstring = data.decode("utf-8")
#     json_acceptable_string = responseInstring.replace("'", "\"")
#     dictionary = json.loads(json_acceptable_string)
#     if (dictionary['status'] == "Success"):
#         lat = (dictionary["details"].get('location_lat'))
#         long = (dictionary["details"].get('location_long'))
#         return dictionary['details']
#         #creatingOutputFile(accountDetail, request, lat, long, filename)
#     else:
#         return (dictionary['status'])
#
#
# def creatingOutputFile(accountDetail, request, lat, long, filename):
#     ftp = ftplib.FTP(accountDetail.ipHost, accountDetail.userName, accountDetail.password)
#     return ftp.getwelcome()
#     # ftp.cwd(str(request.POST['file_path']))
#     # stautusMessage = """ISA*00* *00* *02*SCAC *02*RBINTEST
#     # *100819*1851*U*00401*100110046*0*P*:
#     # GS*QM*SCAC*RBINTEST*20100819*1851*214060250*X*004010
#     # ST*214*0001
#     # B10*3766*9924017*SCAC
#     # MS1***""" + lat+" " + long + """*
#     # SE*10*0002
#     # GE*2*214060250
#     # IEA*1*100110046"""
#     # output = io.BytesIO(str.encode(stautusMessage))
#     # ftp.storbinary('STOR ' + filename + ".edi", output)
